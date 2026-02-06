# FMO-APRS-Remote-Control-Tool

本仓库是一个示范工程，用于演示通过 APRS-IS 发送远程控制指令到设备的报文拼装、签名计算与 ACK 等待逻辑。

包含两份实现：
- C# WinForms：`fmo-aprs-remote-tool/`（图形界面）
- Python：`control.py`（命令行发送器）

本工具发送的 APRS-IS 文本行（单行一帧）形如：
```
<FROM_CALL>-<FROM_SSID>><DEVICE>,<PATH>::<ADDRESSEE_9>:<PAYLOAD>
```

其中：
- `<DEVICE>`：固定为 `APFMO0`
- `<PATH>`：固定为 `TCPIP*`
- `<ADDRESSEE_9>`：目标地址字段，必须右侧补空格到 **9 个字符**（APRS message addressee 规则）
  - 若目标 SSID 为 0：`<TO_CALL>`
  - 若目标 SSID 非 0：`<TO_CALL>-<TO_SSID>`
  - 然后对上述字符串 `PadRight(9, ' ')`

示例（`ADDRESSEE_9` 末尾的空格在等宽字体下可见）：

```
BG5ESN-11>APFMO0,TCPIP*::BD7XYZ-1 :CONTROL,STANDBY,123,0,0011223344556677
```

## 3. 业务载荷（PAYLOAD）格式

`<PAYLOAD>` 为逗号分隔字段：

```
CONTROL,<ACTION>,<T>,<C>,<SIG>
```

字段定义：
- `CONTROL`：固定字符串（type）
- `<ACTION>`：动作字符串（大写）
  - `NORMAL`
  - `STANDBY`
  - `REBOOT`
- `<T>`：Time Slot，**UTC 下 Unix epoch 起算的“分钟数”**
  - 计算：`floor(current_unix_seconds / 60)`
- `<C>`：Counter，计数器（非负整数）
  - 在同一个 `<T>` 内每发送一条指令递增 1
  - 当 `<T>` 变化（进入下一分钟）时重置为 0
  - C# 实现把 `<T>` 与 `<C>` 持久化到本机状态文件，避免重启后重复
  - Python 实现把状态写入 `control_state.json`
- `<SIG>`：签名（见下一节“加密/签名”）

## 4. 加密/签名（重点）

注意：本协议实现中没有对载荷进行“内容加密”（payload 仍是明文），而是使用 **HMAC-SHA1** 做消息认证（防篡改/鉴别请求来源）。

### 4.1 预共享密钥 SECRET

- SECRET 为设备端与发送端共享的字符串,在FMO菜单内可以看见。
- 本示范工程（GUI）对 SECRET 的输入校验为：`^[A-Z0-9]{12}$`（12 位大写字母或数字）。
- 实际签名计算时：
  - 密钥字节序列 `keyBytes = UTF-8(SECRET)`
  - 若 SECRET 为空（C# 中 `null`），则按空字符串处理。

### 4.2 被签名消息（msg）如何拼接

签名输入不是 CSV 整串，也不是带分隔符的字段集合；而是将以下字段**直接拼接**，中间**不包含任何分隔符**：

```
msgRaw = FROM_CALL + FROM_SSID + TYPE + ACTION + T + C
```

其中：
- `FROM_CALL`：发送方呼号（大写）
- `FROM_SSID`：发送方 SSID（整数，十进制字符串，不补零）
- `TYPE`：固定字符串 `CONTROL`
- `ACTION`：动作字符串（如 `STANDBY`）
- `T`：time slot（十进制字符串）
- `C`：counter（十进制字符串）

重要细节（影响互操作）：
- **无分隔符**：例如 `BG5ESN` 和 `11` 拼接后是 `BG5ESN11`。
- 数字字段均按“十进制字符串”拼接：不补零、不固定宽度。
- 字符编码：本工程使用 UTF-8 将 `msgRaw` 编码为字节。

### 4.3 HMAC 算法与截断规则

- 算法：`HMAC-SHA1`
- 输入：
  - `key = UTF-8(SECRET)`
  - `msg = UTF-8(msgRaw)`
- 输出：
  - 先得到 20 字节的 SHA1 HMAC digest
  - 然后取 digest 的**前 8 个字节**（`digest[0..7]`）
  - 最后编码为 **16 个十六进制字符**，并且必须是**大写**

也就是说：

$$SIG = HEXUPPER( HMACSHA1(key, msg)[0..7] )$$

其中 `HEXUPPER` 表示每个字节转 2 位十六进制并使用 `0-9A-F` 大写字母。

欢迎大家根据这个工程，集成进自己的小程序，应用，乃至网站之类。
