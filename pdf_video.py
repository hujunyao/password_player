import sys
import os
import base64

def xor_encrypt(data, key):
    """使用XOR算法加密数据"""
    key_bytes = key.encode('utf-8')
    return bytes([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])

def simple_checksum(password):
    """生成简单的密码校验和"""
    checksum = 0
    for char in password:
        checksum = (checksum + ord(char)) % 10000  # 限制在4位数内
    return str(checksum).zfill(4)  # 补齐4位

def generate_html(video_path, password):
    """生成包含加密视频和密码验证的HTML文件"""
    # 读取视频文件
    with open(video_path, 'rb') as f:
        video_data = f.read()
    
    # 使用XOR加密视频数据
    encrypted_video = xor_encrypt(video_data, password)
    
    # 将加密视频数据转换为Base64以便嵌入HTML
    video_b64 = base64.b64encode(encrypted_video).decode('utf-8')
    
    # 获取视频文件名
    video_name = os.path.basename(video_path)
    
    # 生成简单密码校验和
    password_checksum = simple_checksum(password)
    
    # 获取文件大小
    file_size = len(encrypted_video)
    
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密视频播放器</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            width: 85%;
            max-width: 900px;
            text-align: center;
            display: none; /* 初始隐藏 */
        }}
        .loading-screen {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .loading-logo {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .loading-icon {{
            font-size: 40px;
        }}
        .loading-progress-container {{
            width: 80%;
            max-width: 400px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .loading-progress-bar {{
            width: 0%;
            height: 20px;
            background: linear-gradient(90deg, #00b09b, #96c93d);
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
        .loading-text {{
            font-size: 16px;
            margin-top: 10px;
            color: rgba(255, 255, 255, 0.9);
        }}
        .loading-details {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 5px;
        }}
        h1 {{
            margin-top: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            font-size: 2.2rem;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 1.1rem;
            margin-bottom: 25px;
            opacity: 0.9;
        }}
        .password-form {{
            margin: 25px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }}
        input[type="text"] {{
            padding: 12px 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50px;
            background: rgba(255, 255, 255, 0.15);
            color: white;
            font-size: 16px;
            width: 70%;
            max-width: 350px;
            outline: none;
            transition: all 0.3s ease;
        }}
        input[type="text"]:focus {{
            border-color: rgba(255, 255, 255, 0.7);
            background: rgba(255, 255, 255, 0.25);
        }}
        input[type="text"]::placeholder {{
            color: rgba(255, 255, 255, 0.7);
        }}
        button {{
            padding: 12px 30px;
            border: none;
            border-radius: 50px;
            background: linear-gradient(90deg, #ff416c, #ff4b2b);
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            margin: 5px;
        }}
        button:hover, button:active {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }}
        .download-btn {{
            background: linear-gradient(90deg, #2193b0, #6dd5ed);
        }}
        .play-btn {{
            background: linear-gradient(90deg, #38ef7d, #11998e);
        }}
        .video-container {{
            display: none;
            margin-top: 25px;
            width: 100%;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }}
        video {{
            width: 100%;
            display: block;
        }}
        .error {{
            color: #ff6b6b;
            margin-top: 12px;
            display: none;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
        }}
        .processing-message {{
            display: none;
            margin-top: 12px;
            color: #fff;
            font-size: 14px;
        }}
        .action-buttons {{
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .instructions {{
            margin-top: 25px;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.5;
        }}
        .logo {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .logo-icon {{
            font-size: 32px;
        }}
        .footer {{
            margin-top: 35px;
            font-size: 13px;
            opacity: 0.7;
        }}
        .mobile-warning {{
            display: none;
            background: rgba(255, 193, 7, 0.2);
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 15px 0;
            border-radius: 5px;
            text-align: left;
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                width: 90%;
            }}
            input[type="text"] {{
                width: 90%;
                padding: 10px 18px;
                font-size: 15px;
            }}
            button {{
                padding: 10px 25px;
                font-size: 15px;
                width: 100%;
            }}
            .action-buttons {{
                flex-direction: column;
                align-items: center;
            }}
            .mobile-warning {{
                display: block;
            }}
            .loading-progress-container {{
                width: 90%;
            }}
        }}
    </style>
</head>
<body>
    <!-- 加载屏幕 -->
    <div class="loading-screen" id="loadingScreen">
        <div class="loading-logo">
            <span class="loading-icon">🔒</span>
            <span>安全视频播放系统</span>
        </div>
        <div class="loading-progress-container">
            <div class="loading-progress-bar" id="loadingProgressBar"></div>
        </div>
        <div class="loading-text" id="loadingText">正在加载视频数据...</div>
        <div class="loading-details" id="loadingDetails">0% - 准备中</div>
    </div>

    <!-- 主内容容器 -->
    <div class="container" id="mainContainer">
        <div class="logo">
            <span class="logo-icon">🔒</span>
            <span>安全视频播放系统</span>
        </div>
        
        <h1>加密视频内容</h1>
        <div class="subtitle">请输入密码解锁视频</div>
        
        <div class="mobile-warning">
            <strong>移动设备提示:</strong> 大文件处理需要时间，请耐心等待。
        </div>
        
        <div class="password-form">
            <input type="text" id="passwordInput" placeholder="请输入访问密码...">
            <button id="decryptButton">验证密码</button>
        </div>
        
        <div id="errorMessage" class="error">密码错误，请重试！</div>
        <div id="processingMessage" class="processing-message">正在处理，请稍候...</div>
        
        <div id="actionContainer" class="action-buttons" style="display: none;">
            <button id="downloadButton" class="download-btn">下载视频</button>
            <button id="playButton" class="play-btn">播放视频</button>
        </div>
        
        <div id="videoContainer" class="video-container">
            <video id="videoPlayer" controls playsinline></video>
        </div>
        
        <div class="instructions">
            <p>🔐 此视频内容已使用加密技术进行保护</p>
            <p>📁 文件大小: {file_size//(1024*1024)}MB</p>
            <p>📱 支持电脑和移动设备播放</p>
        </div>

        <div class="footer">
            <p>安全视频播放系统</p>
        </div>
    </div>

    <script>
        // 加密的视频数据（Base64编码）
        const encryptedVideoBase64 = "{video_b64}";
        const correctPasswordChecksum = "{password_checksum}";
        const videoName = "{video_name}";
        const totalFileSize = {file_size};
        
        // 全局变量
        let decryptedVideoData = null;
        let isProcessing = false;
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            // 开始加载进度
            simulateLoadingProgress();
            
            // 添加按钮点击事件
            document.getElementById('decryptButton').addEventListener('click', validatePassword);
            document.getElementById('downloadButton').addEventListener('click', downloadVideo);
            document.getElementById('playButton').addEventListener('click', playVideo);
            
            // 支持按回车键提交密码
            document.getElementById('passwordInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    validatePassword();
                }}
            }});
        }});
        
        // 模拟加载进度
        function simulateLoadingProgress() {{
            const progressBar = document.getElementById('loadingProgressBar');
            const loadingText = document.getElementById('loadingText');
            const loadingDetails = document.getElementById('loadingDetails');
            const loadingScreen = document.getElementById('loadingScreen');
            const mainContainer = document.getElementById('mainContainer');
            
            let progress = 0;
            const totalSteps = 100;
            const fileSizeMB = Math.round(totalFileSize / (1024 * 1024));
            
            const interval = setInterval(function() {{
                progress += 1;
                if (progress <= 85) {{
                    // 前期快速加载
                    progressBar.style.width = progress + '%';
                    loadingDetails.textContent = progress + '% - 加载基础资源';
                }} else if (progress <= 95) {{
                    // 中期中等速度
                    progress += 0.5;
                    progressBar.style.width = progress + '%';
                    loadingDetails.textContent = progress + '% - 处理视频数据';
                }} else {{
                    // 后期慢速完成
                    progress += 0.2;
                    progressBar.style.width = progress + '%';
                    loadingDetails.textContent = progress + '% - 最终优化';
                }}
                
                if (progress >= 100) {{
                    clearInterval(interval);
                    progressBar.style.width = '100%';
                    loadingText.textContent = '加载完成！';
                    loadingDetails.textContent = '100% - 准备就绪';
                    
                    // 延迟显示主界面
                    setTimeout(function() {{
                        loadingScreen.style.display = 'none';
                        mainContainer.style.display = 'block';
                        
                        // 自动聚焦到密码输入框
                        document.getElementById('passwordInput').focus();
                    }}, 500);
                }}
            }}, 50);
        }}
        
        // 简单的校验和函数
        function simpleChecksum(password) {{
            let checksum = 0;
            for (let i = 0; i < password.length; i++) {{
                checksum = (checksum + password.charCodeAt(i)) % 10000;
            }}
            return checksum.toString().padStart(4, '0');
        }}
        
        function validatePassword() {{
            const password = document.getElementById('passwordInput').value;
            const errorMessage = document.getElementById('errorMessage');
            const actionContainer = document.getElementById('actionContainer');
            const processingMessage = document.getElementById('processingMessage');
            
            if (isProcessing) return;
            
            // 验证密码
            if (!password) {{
                showError('请输入密码！');
                return;
            }}
            
            // 计算输入密码的校验和
            const inputChecksum = simpleChecksum(password);
            if (inputChecksum !== correctPasswordChecksum) {{
                showError('密码错误，请重试！');
                return;
            }}
            
            // 密码正确，显示操作按钮
            errorMessage.style.display = 'none';
            actionContainer.style.display = 'flex';
        }}
        
        async function downloadVideo() {{
            if (isProcessing) return;
            isProcessing = true;
            
            const password = document.getElementById('passwordInput').value;
            const processingMessage = document.getElementById('processingMessage');
            const actionContainer = document.getElementById('actionContainer');
            
            // 显示处理消息，隐藏操作按钮
            actionContainer.style.display = 'none';
            processingMessage.style.display = 'block';
            processingMessage.textContent = '正在解密并准备下载，请稍候...';
            
            try {{
                // 解码Base64数据
                const encryptedData = base64ToUint8Array(encryptedVideoBase64);
                
                // 解密数据
                decryptedVideoData = xorDecrypt(encryptedData, password);
                
                // 创建Blob对象
                const videoBlob = new Blob([decryptedVideoData], {{ type: 'video/mp4' }});
                const videoUrl = URL.createObjectURL(videoBlob);
                
                // 创建下载链接
                const a = document.createElement('a');
                a.href = videoUrl;
                a.download = videoName;
                document.body.appendChild(a);
                a.click();
                
                // 清理
                setTimeout(function() {{
                    document.body.removeChild(a);
                    URL.revokeObjectURL(videoUrl);
                    processingMessage.style.display = 'none';
                    actionContainer.style.display = 'flex';
                    isProcessing = false;
                }}, 100);
                
            }} catch (error) {{
                processingMessage.style.display = 'none';
                actionContainer.style.display = 'flex';
                showError('下载失败：' + error.message);
                isProcessing = false;
            }}
        }}
        
        async function playVideo() {{
            if (isProcessing) return;
            isProcessing = true;
            
            const password = document.getElementById('passwordInput').value;
            const videoContainer = document.getElementById('videoContainer');
            const processingMessage = document.getElementById('processingMessage');
            const actionContainer = document.getElementById('actionContainer');
            
            // 显示处理消息，隐藏操作按钮
            actionContainer.style.display = 'none';
            processingMessage.style.display = 'block';
            processingMessage.textContent = '正在解密并准备播放，请稍候...';
            
            try {{
                // 如果尚未解密，先解密视频
                if (!decryptedVideoData) {{
                    const encryptedData = base64ToUint8Array(encryptedVideoBase64);
                    decryptedVideoData = xorDecrypt(encryptedData, password);
                }}
                
                // 创建Blob并设置视频源
                const videoBlob = new Blob([decryptedVideoData], {{ type: 'video/mp4' }});
                const videoUrl = URL.createObjectURL(videoBlob);
                
                const videoPlayer = document.getElementById('videoPlayer');
                videoPlayer.src = videoUrl;
                videoContainer.style.display = 'block';
                processingMessage.style.display = 'none';
                actionContainer.style.display = 'flex';
                
                // 滚动到视频位置
                videoContainer.scrollIntoView({{ behavior: 'smooth' }});
                
                isProcessing = false;
                
            }} catch (error) {{
                processingMessage.style.display = 'none';
                actionContainer.style.display = 'flex';
                showError('播放失败：' + error.message);
                isProcessing = false;
            }}
        }}
        
        function showError(message) {{
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }}
        
        // Base64转Uint8Array
        function base64ToUint8Array(base64) {{
            const binaryString = atob(base64);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {{
                bytes[i] = binaryString.charCodeAt(i);
            }}
            return bytes;
        }}
        
        // XOR解密函数
        function xorDecrypt(data, key) {{
            const keyBytes = new TextEncoder().encode(key);
            const result = new Uint8Array(data.length);
            
            for (let i = 0; i < data.length; i++) {{
                result[i] = data[i] ^ keyBytes[i % keyBytes.length];
            }}
            
            return result;
        }}
    </script>
</body>
</html>
'''
    return html_content

def main():
    if len(sys.argv) != 3:
        print("用法: python video_encrypt.py <密码> <视频文件>")
        print("示例: python video_encrypt.py mypassword video.mp4")
        sys.exit(1)
    
    password = sys.argv[1]
    video_file = sys.argv[2]
    
    if not os.path.exists(video_file):
        print(f"错误: 文件 '{video_file}' 不存在")
        sys.exit(1)
    
    if not video_file.lower().endswith('.mp4'):
        print("警告: 建议使用MP4格式视频文件以获得最佳兼容性")
    
    # 显示文件大小信息
    file_size = os.path.getsize(video_file) / (1024 * 1024)  # MB
    print(f"视频文件大小: {file_size:.1f}MB")
    if file_size > 50:
        print("提示: 大文件加载需要时间，已添加加载进度条")
    
    print("生成HTML页面...")
    html_content = generate_html(video_file, password)
    
    # 保存HTML文件
    output_file = "encrypted_video_player.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"已生成加密视频播放网页: {output_file}")
    print("请使用现代浏览器打开此文件")
    print("注意: 网页加载时会显示进度条，请耐心等待")

if __name__ == "__main__":
    main()