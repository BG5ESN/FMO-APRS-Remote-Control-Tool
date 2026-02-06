using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;

namespace fmo_aprs_remote_tool
{
    public partial class FMOAPRSRemoteControl : Form
    {
        private readonly Controler _controler = new Controler();

        public FMOAPRSRemoteControl()
        {
            InitializeComponent();
            this.button_normal.Click += new System.EventHandler(this.button_normal_Click);
            this.button_reboot.Click += new System.EventHandler(this.button_reboot_Click);
        }

        private void textBox_loginCallWithSSID_TextChanged(object sender, EventArgs e)
        {
            //检查：呼号格式:必须是XXXXX-XX
            TextBox textBox = sender as TextBox;
            if (textBox == null) return;

            string input = textBox.Text;

            // 空值时不验证，允许用户正在输入
            if (string.IsNullOrEmpty(input))
            {
                textBox.BackColor = SystemColors.Window;
                return;
            }
            bool notEuqal = !(input == this.textBox_toCallWithSSID.Text);
            bool pass = ValidationHelper.IsValidCallsign(input); 
            bool isValid = notEuqal && pass;
            // 根据验证结果设置背景颜色
            textBox.BackColor = isValid ? SystemColors.Window : Color.LightPink;
        }

        private void textBox_passcode_TextChanged(object sender, EventArgs e)
        {
            //检查: 必须是五位纯数字
            TextBox textBox = sender as TextBox;
            if (textBox == null) return;

            string input = textBox.Text;

            // 空值时不验证，允许用户正在输入
            if (string.IsNullOrEmpty(input))
            {
                textBox.BackColor = SystemColors.Window;
                return;
            }

            // 使用 ValidationHelper 验证密码格式
            bool isValid = ValidationHelper.IsValidPasscode(input);

            // 根据验证结果设置背景颜色
            textBox.BackColor = isValid ? SystemColors.Window : Color.LightPink;
        }

        private void textBox_secrect_TextChanged(object sender, EventArgs e)
        {
            // 必须是长度为12的大写字母+数字的组合体
            TextBox textBox = sender as TextBox;
            if (textBox == null) return;

            string input = textBox.Text;

            // 空值时不验证，允许用户正在输入
            if (string.IsNullOrEmpty(input))
            {
                textBox.BackColor = SystemColors.Window;
                return;
            }

            // 使用 ValidationHelper 验证密钥格式
            bool isValid = ValidationHelper.IsValidSecret(input);

            // 根据验证结果设置背景颜色
            textBox.BackColor = isValid ? SystemColors.Window : Color.LightPink;
        }

        private void textBox_toCallWithSSID_TextChanged(object sender, EventArgs e)
        {
            //和登录呼号一样的验证规则,但不能和登录呼号一致
            TextBox textBox = sender as TextBox;
            if (textBox == null) return;

            string input = textBox.Text;

            // 空值时不验证，允许用户正在输入
            if (string.IsNullOrEmpty(input))
            {
                textBox.BackColor = SystemColors.Window;
                return;
            }

            bool notEuqal = !(input == this.textBox_loginCallWithSSID.Text);
            bool pass = ValidationHelper.IsValidCallsign(input);
            bool isValid = notEuqal && pass;
            // 根据验证结果设置背景颜色
            textBox.BackColor = isValid ? SystemColors.Window : Color.LightPink;
        }

        private void button_standby_Click(object sender, EventArgs e)
        {
            StartSend(Controler.CMD.STANDBY);
        }

        private void button_normal_Click(object sender, EventArgs e)
        {
            StartSend(Controler.CMD.NORMAL);
        }

        private void button_reboot_Click(object sender, EventArgs e)
        {
            StartSend(Controler.CMD.REBOOT);
        }

        private void StartSend(Controler.CMD cmd)
        {
            string login = this.textBox_loginCallWithSSID.Text;
            string toCall = this.textBox_toCallWithSSID.Text;
            string passcode = this.textBox_passcode.Text;
            string secret = this.textBox_secrect.Text;

            if (!ValidationHelper.IsValidCallsign(login))
            {
                this.label_helper.Text = "登录呼号格式不正确";
                return;
            }
            if (!ValidationHelper.IsValidToCallsign(toCall, login))
            {
                this.label_helper.Text = "目标呼号格式不正确，或与登录呼号相同";
                return;
            }
            if (!ValidationHelper.IsValidPasscode(passcode))
            {
                this.label_helper.Text = "PASSCODE 格式不正确";
                return;
            }
            if (!ValidationHelper.IsValidSecret(secret))
            {
                this.label_helper.Text = "密钥格式不正确";
                return;
            }

            SetUiBusy(true, "发送中..." + cmd.ToString());

            ThreadPool.QueueUserWorkItem(delegate
            {
                Controler.ACKType result = _controler.SendAprsCmd(login, passcode, secret, toCall, cmd);
                string msg;
                switch (result)
                {
                    case Controler.ACKType.ACK_SUCC:
                        msg = "ACK 成功";
                        break;
                    case Controler.ACKType.ACK_FAIL:
                        msg = "ACK 失败";
                        break;
                    case Controler.ACKType.PASSCODEERROR:
                        msg = "PASSCODE 错误（APRS-IS 登录未验证）";
                        break;
                    case Controler.ACKType.TIMEOUT:
                    default:
                        msg = "超时未收到 ACK";
                        break;
                }

                try
                {
                    this.BeginInvoke((MethodInvoker)delegate
                    {
                        SetUiBusy(false, msg);
                    });
                }
                catch
                {
                    // ignore
                }
            });
        }

        private void SetUiBusy(bool busy, string message)
        {
            this.button_standby.Enabled = !busy;
            this.button_normal.Enabled = !busy;
            this.button_reboot.Enabled = !busy;
            this.Cursor = busy ? Cursors.WaitCursor : Cursors.Default;
            this.label_helper.Text = message;
        }
    }
}
