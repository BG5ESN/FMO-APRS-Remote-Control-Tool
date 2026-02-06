using System;
using System.IO;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;

namespace fmo_aprs_remote_tool
{
    public class Controler
    {
        private const string DefaultHost = "china.aprs2.net";
        private const int DefaultPort = 14580;
        private const string DefaultDevice = "APFMO0";
        private const string DefaultPath = "TCPIP*";

        private const double DefaultAckWaitSeconds = 6.0;

        public enum ACKType
        {
            TIMEOUT,//超时无ACK
            PASSCODEERROR, //PASSCODE错误,无法发送指令
            ACK_SUCC, //ACK回复成功
            ACK_FAIL, // ACK回复失败
        };
        public enum CMD
        {
            REBOOT,
            STANDBY,
            NORMAL
        };

        public ACKType sendAprsCmd(string callsignWithSSID, string passcode, string secrect, string tocallWithSSID)
        {
            return SendAprsCmd(callsignWithSSID, passcode, secrect, tocallWithSSID, CMD.STANDBY, DefaultAckWaitSeconds);
        }

        public ACKType SendAprsCmd(string callsignWithSSID, string passcode, string secrect, string tocallWithSSID, CMD cmd)
        {
            return SendAprsCmd(callsignWithSSID, passcode, secrect, tocallWithSSID, cmd, DefaultAckWaitSeconds);
        }

        public ACKType SendAprsCmd(string callsignWithSSID, string passcode, string secrect, string tocallWithSSID, CMD cmd, double ackWaitSeconds)
        {
            try
            {
                string fromCall;
                int fromSsid;
                ParseCallsignSsid(callsignWithSSID, out fromCall, out fromSsid);

                string toCall;
                int toSsid;
                if (string.IsNullOrEmpty(tocallWithSSID))
                {
                    toCall = fromCall;
                    toSsid = fromSsid;
                }
                else
                {
                    ParseCallsignSsid(tocallWithSSID, out toCall, out toSsid);
                }

                string action = CmdToAction(cmd);
                int timeSlot = GetCurrentTimeSlotMinutes();
                int counter = NextCounter(timeSlot);

                string sig = CalcSignature(fromCall, fromSsid, "CONTROL", action, timeSlot, counter, secrect);
                string payload = "CONTROL," + action + "," + timeSlot + "," + counter + "," + sig;

                string addressee = FormatAddressee(toCall, toSsid);
                string raw = fromCall + "-" + fromSsid + ">" + DefaultDevice + "," + DefaultPath + "::" + addressee + ":" + payload;

                using (TcpClient client = new TcpClient())
                {
                    client.ReceiveTimeout = 500;
                    client.SendTimeout = 5000;
                    client.Connect(DefaultHost, DefaultPort);

                    using (NetworkStream stream = client.GetStream())
                    {
                        stream.ReadTimeout = 500;
                        stream.WriteTimeout = 5000;

                        string login = "user " + fromCall + "-" + fromSsid + " pass " + passcode + " vers FMO-CTRL 0.1";
                        SendLine(stream, login);

                        // 等待服务器 logresp，判定 passcode 是否有效（尽量不复杂，给 2s）
                        DateTime loginEnd = DateTime.UtcNow.AddMilliseconds(2000);
                        while (DateTime.UtcNow < loginEnd)
                        {
                            string line = TryReadLine(stream);
                            if (line == null) continue;
                            if (line.IndexOf("logresp", StringComparison.OrdinalIgnoreCase) >= 0)
                            {
                                if (line.IndexOf("unverified", StringComparison.OrdinalIgnoreCase) >= 0)
                                    return ACKType.PASSCODEERROR;
                                break;
                            }
                        }

                        SendLine(stream, raw);

                        if (ackWaitSeconds <= 0)
                            return ACKType.TIMEOUT;

                        DateTime end = DateTime.UtcNow.AddMilliseconds((int)(ackWaitSeconds * 1000));
                        while (DateTime.UtcNow < end)
                        {
                            string line = TryReadLine(stream);
                            if (line == null) continue;

                            // Python 端逻辑：包含 ":ACK,CONTROL," 或 "ACK,CONTROL," 视为 ACK
                            if (line.IndexOf(":ACK,CONTROL,", StringComparison.OrdinalIgnoreCase) >= 0 ||
                                line.IndexOf("ACK,CONTROL,", StringComparison.OrdinalIgnoreCase) >= 0)
                            {
                                // 若固件/网关带 FAIL/NACK 语义，尽量区分
                                if (line.IndexOf("NACK", StringComparison.OrdinalIgnoreCase) >= 0 ||
                                    line.IndexOf("FAIL", StringComparison.OrdinalIgnoreCase) >= 0)
                                    return ACKType.ACK_FAIL;
                                return ACKType.ACK_SUCC;
                            }
                        }

                        return ACKType.TIMEOUT;
                    }
                }
            }
            catch
            {
                return ACKType.TIMEOUT;
            }
        }

        private static string CmdToAction(CMD cmd)
        {
            switch (cmd)
            {
                case CMD.NORMAL:
                    return "NORMAL";
                case CMD.REBOOT:
                    return "REBOOT";
                case CMD.STANDBY:
                default:
                    return "STANDBY";
            }
        }

        private static void ParseCallsignSsid(string callsignWithSsid, out string call, out int ssid)
        {
            if (callsignWithSsid == null)
                throw new ArgumentNullException("callsignWithSsid");

            string s = callsignWithSsid.Trim().ToUpperInvariant();
            if (s.Length == 0)
                throw new ArgumentException("callsign is empty");

            int dash = s.IndexOf('-');
            if (dash >= 0)
            {
                call = s.Substring(0, dash);
                string ssidStr = s.Substring(dash + 1);
                if (call.Length == 0)
                    throw new ArgumentException("callsign missing before '-'");
                if (ssidStr.Length == 0)
                    throw new ArgumentException("SSID missing after '-'");
                ssid = int.Parse(ssidStr);
            }
            else
            {
                call = s;
                ssid = 0;
            }

            if (ssid < 0 || ssid > 15)
                throw new ArgumentOutOfRangeException("ssid", "SSID out of range (0~15)");
        }

        private static string FormatAddressee(string toCall, int toSsid)
        {
            string addr = (toSsid != 0) ? (toCall + "-" + toSsid) : toCall;
            if (addr.Length > 9)
                throw new ArgumentException("TO addressee too long: " + addr);
            return addr.PadRight(9, ' ');
        }

        private static int GetCurrentTimeSlotMinutes()
        {
            DateTime epoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            TimeSpan ts = DateTime.UtcNow.Subtract(epoch);
            long seconds = (long)ts.TotalSeconds;
            return (int)(seconds / 60);
        }

        private static string CalcSignature(string fromCall, int fromSsid, string typeStr, string actionStr, int timeSlot, int counter, string secret)
        {
            // SIGNATURE = HMAC-SHA1(key=SECRET, msg=CALL+SSID+TYPE+ACTION+T+C)
            string raw = fromCall + fromSsid + typeStr + actionStr + timeSlot + counter;
            byte[] key = Encoding.UTF8.GetBytes(secret ?? string.Empty);
            byte[] msg = Encoding.UTF8.GetBytes(raw);
            using (HMACSHA1 hmac = new HMACSHA1(key))
            {
                byte[] digest = hmac.ComputeHash(msg);
                // first 8 bytes
                byte[] first8 = new byte[8];
                Buffer.BlockCopy(digest, 0, first8, 0, 8);
                return ToHexUpper(first8);
            }
        }

        private static string ToHexUpper(byte[] data)
        {
            const string hex = "0123456789ABCDEF";
            StringBuilder sb = new StringBuilder(data.Length * 2);
            for (int i = 0; i < data.Length; i++)
            {
                byte b = data[i];
                sb.Append(hex[(b >> 4) & 0xF]);
                sb.Append(hex[b & 0xF]);
            }
            return sb.ToString();
        }

        private static void SendLine(NetworkStream stream, string line)
        {
            if (line == null) line = string.Empty;
            if (!line.EndsWith("\n"))
                line += "\n";
            byte[] bytes = Encoding.UTF8.GetBytes(line);
            stream.Write(bytes, 0, bytes.Length);
            stream.Flush();
        }

        private static string TryReadLine(NetworkStream stream)
        {
            // 简易逐行读取：ReadTimeout=500ms；超时返回 null
            try
            {
                StringBuilder sb = new StringBuilder();
                while (true)
                {
                    int b = stream.ReadByte();
                    if (b < 0) return null;
                    if (b == '\n') break;
                    if (b == '\r') continue;
                    sb.Append((char)b);
                    // 保护：避免异常超长行
                    if (sb.Length > 8192) break;
                }

                string s = sb.ToString();
                if (s.Trim().Length == 0) return null;
                return s;
            }
            catch (IOException)
            {
                return null;
            }
            catch (ObjectDisposedException)
            {
                return null;
            }
        }

        private static string GetStateFilePath()
        {
            string dir = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            if (dir == null || dir.Length == 0)
                dir = AppDomain.CurrentDomain.BaseDirectory;

            string folder = Path.Combine(dir, "fmo-aprs-remote-tool");
            try { Directory.CreateDirectory(folder); }
            catch { }

            return Path.Combine(folder, "control_state.txt");
        }

        private static int NextCounter(int timeSlot)
        {
            string path = GetStateFilePath();
            int lastTs;
            int lastC;
            ReadState(path, out lastTs, out lastC);

            int c = (lastTs == timeSlot) ? (lastC + 1) : 0;
            WriteState(path, timeSlot, c);
            return c;
        }

        private static void ReadState(string path, out int timeSlot, out int counter)
        {
            timeSlot = int.MinValue;
            counter = -1;
            try
            {
                if (!File.Exists(path)) return;
                string[] lines = File.ReadAllLines(path, Encoding.UTF8);
                for (int i = 0; i < lines.Length; i++)
                {
                    string line = lines[i];
                    if (line == null) continue;
                    int eq = line.IndexOf('=');
                    if (eq <= 0) continue;
                    string k = line.Substring(0, eq).Trim();
                    string v = line.Substring(eq + 1).Trim();
                    if (k.Equals("time_slot", StringComparison.OrdinalIgnoreCase))
                        timeSlot = int.Parse(v);
                    else if (k.Equals("counter", StringComparison.OrdinalIgnoreCase))
                        counter = int.Parse(v);
                }
            }
            catch
            {
                timeSlot = int.MinValue;
                counter = -1;
            }
        }

        private static void WriteState(string path, int timeSlot, int counter)
        {
            try
            {
                string content = "time_slot=" + timeSlot + Environment.NewLine + "counter=" + counter + Environment.NewLine;
                File.WriteAllText(path, content, Encoding.UTF8);
            }
            catch
            {
                // ignore
            }
        }
    }
}
