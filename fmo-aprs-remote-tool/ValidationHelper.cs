using System;
using System.Text.RegularExpressions;

namespace fmo_aprs_remote_tool
{
    public static class ValidationHelper
    {
        // 验证呼号格式：5-6个字符（必须包含至少一个数字）+ 连字符 + 2位数字
        public static bool IsValidCallsign(string callsign)
        {
            if (string.IsNullOrEmpty(callsign)) return false;
            return Regex.IsMatch(callsign, @"^(?=[A-Z0-9]*[0-9])[A-Z0-9]{5,6}-[0-9]{1,2}$");
        }
        
        // 验证密码格式：5位纯数字
        public static bool IsValidPasscode(string passcode)
        {
            if (string.IsNullOrEmpty(passcode)) return false;
            return Regex.IsMatch(passcode, @"^\d{5}$");
        }
        
        // 验证密钥格式：12位大写字母和数字组合
        public static bool IsValidSecret(string secret)
        {
            if (string.IsNullOrEmpty(secret)) return false;
            return Regex.IsMatch(secret, @"^[A-Z0-9]{12}$");
        }
        
        // 验证目标呼号：格式正确且不与登录呼号相同
        public static bool IsValidToCallsign(string toCallsign, string loginCallsign)
        {
            if (string.IsNullOrEmpty(toCallsign)) return false;
            if (!IsValidCallsign(toCallsign)) return false;
            return !toCallsign.Equals(loginCallsign, StringComparison.OrdinalIgnoreCase);
        }
    }
}