namespace fmo_aprs_remote_tool
{
    partial class FMOAPRSRemoteControl
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.textBox_loginCallWithSSID = new System.Windows.Forms.TextBox();
            this.textBox_passcode = new System.Windows.Forms.TextBox();
            this.textBox_secrect = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.button_standby = new System.Windows.Forms.Button();
            this.button_normal = new System.Windows.Forms.Button();
            this.button_reboot = new System.Windows.Forms.Button();
            this.label_ack = new System.Windows.Forms.Label();
            this.textBox_toCallWithSSID = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.label_helper = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(30, 21);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(107, 12);
            this.label1.TabIndex = 0;
            this.label1.Text = "登录呼号(带尾缀):";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(78, 48);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(59, 12);
            this.label2.TabIndex = 1;
            this.label2.Text = "PASSCODE:";
            // 
            // textBox_loginCallWithSSID
            // 
            this.textBox_loginCallWithSSID.Location = new System.Drawing.Point(143, 18);
            this.textBox_loginCallWithSSID.Name = "textBox_loginCallWithSSID";
            this.textBox_loginCallWithSSID.Size = new System.Drawing.Size(197, 21);
            this.textBox_loginCallWithSSID.TabIndex = 2;
            this.textBox_loginCallWithSSID.TextChanged += new System.EventHandler(this.textBox_loginCallWithSSID_TextChanged);
            // 
            // textBox_passcode
            // 
            this.textBox_passcode.Location = new System.Drawing.Point(143, 45);
            this.textBox_passcode.Name = "textBox_passcode";
            this.textBox_passcode.Size = new System.Drawing.Size(197, 21);
            this.textBox_passcode.TabIndex = 3;
            this.textBox_passcode.TextChanged += new System.EventHandler(this.textBox_passcode_TextChanged);
            // 
            // textBox_secrect
            // 
            this.textBox_secrect.Location = new System.Drawing.Point(143, 72);
            this.textBox_secrect.Name = "textBox_secrect";
            this.textBox_secrect.Size = new System.Drawing.Size(197, 21);
            this.textBox_secrect.TabIndex = 4;
            this.textBox_secrect.TextChanged += new System.EventHandler(this.textBox_secrect_TextChanged);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(53, 75);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(83, 12);
            this.label3.TabIndex = 5;
            this.label3.Text = "APRS远控密钥:";
            // 
            // button_standby
            // 
            this.button_standby.Location = new System.Drawing.Point(103, 158);
            this.button_standby.Name = "button_standby";
            this.button_standby.Size = new System.Drawing.Size(75, 23);
            this.button_standby.TabIndex = 6;
            this.button_standby.Text = "待机";
            this.button_standby.UseVisualStyleBackColor = true;
            this.button_standby.Click += new System.EventHandler(this.button_standby_Click);
            // 
            // button_normal
            // 
            this.button_normal.Location = new System.Drawing.Point(184, 158);
            this.button_normal.Name = "button_normal";
            this.button_normal.Size = new System.Drawing.Size(75, 23);
            this.button_normal.TabIndex = 7;
            this.button_normal.Text = "正常";
            this.button_normal.UseVisualStyleBackColor = true;
            // 
            // button_reboot
            // 
            this.button_reboot.Location = new System.Drawing.Point(265, 158);
            this.button_reboot.Name = "button_reboot";
            this.button_reboot.Size = new System.Drawing.Size(75, 23);
            this.button_reboot.TabIndex = 8;
            this.button_reboot.Text = "重启";
            this.button_reboot.UseVisualStyleBackColor = true;
            // 
            // label_ack
            // 
            this.label_ack.AutoSize = true;
            this.label_ack.Location = new System.Drawing.Point(12, 127);
            this.label_ack.Name = "label_ack";
            this.label_ack.Size = new System.Drawing.Size(35, 12);
            this.label_ack.TabIndex = 9;
            this.label_ack.Text = "报告:";
            // 
            // textBox_toCallWithSSID
            // 
            this.textBox_toCallWithSSID.Location = new System.Drawing.Point(143, 99);
            this.textBox_toCallWithSSID.Name = "textBox_toCallWithSSID";
            this.textBox_toCallWithSSID.Size = new System.Drawing.Size(197, 21);
            this.textBox_toCallWithSSID.TabIndex = 11;
            this.textBox_toCallWithSSID.TextChanged += new System.EventHandler(this.textBox_toCallWithSSID_TextChanged);
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(35, 102);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(101, 12);
            this.label5.TabIndex = 12;
            this.label5.Text = "FMO呼号(带尾缀):";
            // 
            // label_helper
            // 
            this.label_helper.AutoSize = true;
            this.label_helper.Location = new System.Drawing.Point(53, 127);
            this.label_helper.Name = "label_helper";
            this.label_helper.Size = new System.Drawing.Size(29, 12);
            this.label_helper.TabIndex = 10;
            this.label_helper.Text = "暂无";
            // 
            // FMOAPRSRemoteControl
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(352, 195);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.textBox_toCallWithSSID);
            this.Controls.Add(this.label_helper);
            this.Controls.Add(this.label_ack);
            this.Controls.Add(this.button_reboot);
            this.Controls.Add(this.button_normal);
            this.Controls.Add(this.button_standby);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.textBox_secrect);
            this.Controls.Add(this.textBox_passcode);
            this.Controls.Add(this.textBox_loginCallWithSSID);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.MaximizeBox = false;
            this.MaximumSize = new System.Drawing.Size(368, 234);
            this.MinimizeBox = false;
            this.MinimumSize = new System.Drawing.Size(368, 234);
            this.Name = "FMOAPRSRemoteControl";
            this.ShowIcon = false;
            this.Text = "FMO APRS 远控程序";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox textBox_loginCallWithSSID;
        private System.Windows.Forms.TextBox textBox_passcode;
        private System.Windows.Forms.TextBox textBox_secrect;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Button button_standby;
        private System.Windows.Forms.Button button_normal;
        private System.Windows.Forms.Button button_reboot;
        private System.Windows.Forms.Label label_ack;
        private System.Windows.Forms.TextBox textBox_toCallWithSSID;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label label_helper;
    }
}

