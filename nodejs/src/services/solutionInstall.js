const { handleError } = require('../utils/helper');
const { spawn } = require('child_process');

function runBash(command, options = {}) {
    return new Promise((resolve, reject) => {
        const child = spawn('sh', ['-c', command], options);
        child.stdout.on('data', (data) => console.log(String(data).trim()));
        child.stderr.on('data', (data) => console.error(String(data).trim()));
        child.on('close', (code) => {
            return code === 0 ? resolve(code) : reject(new Error(`Command failed: ${command}`));
        });
    });
}

function runBashWithProgress(command, res, progressMessage) {
    return new Promise((resolve, reject) => {
        // Send progress update
        if (res && progressMessage) {
            res.write(`data: ${JSON.stringify({ 
                type: 'progress', 
                message: progressMessage,
                timestamp: new Date().toISOString()
            })}\n\n`);
        }

        const child = spawn('sh', ['-c', command], {});
        
        child.stdout.on('data', (data) => {
            const output = String(data).trim();
            console.log(output);
            
            // Send real-time output to client
            if (res) {
                res.write(`data: ${JSON.stringify({ 
                    type: 'output', 
                    message: output,
                    timestamp: new Date().toISOString()
                })}\n\n`);
            }
        });
        
        child.stderr.on('data', (data) => {
            const error = String(data).trim();
            console.error(error);
            
            // Send error output to client
            if (res) {
                res.write(`data: ${JSON.stringify({ 
                    type: 'error_output', 
                    message: error,
                    timestamp: new Date().toISOString()
                })}\n\n`);
            }
        });
        
        child.on('close', (code) => {
            if (code === 0) {
                resolve(code);
            } else {
                reject(new Error(`Command failed: ${command}`));
            }
        });
    });
}

const install = async (req) => {
    try {
        console.log('✅ Static Data: Solution install function running...');
        console.log({ id: 1, name: 'Test Solution', status: 'Started' });

        const repoUrl = 'https://github.com/devweam-ai/ai-doc-editor.git';
        const repoName = 'ai-doc-editor';
        const repoPath = `/workspace/${repoName}`;
        const imageName = 'ai-doc-editor-img';
        const containerName = 'ai-doc-editor-container';
        const networkName = 'weamai_app-network';
        const port = '3002';
        const branchName = 'mongodb';

        // await runBash(`rm -rf ${repoPath} && git clone -b ${branchName} ${repoUrl} ${repoPath}`);
        await runBash(`rm -rf ${repoPath}`);
        await runBash(`git clone -b ${branchName} ${repoUrl} ${repoPath}`);

        await runBash(`cp ${repoPath}/env.example ${repoPath}/.env`);
        
        await runBash(`docker build -t ${imageName} ${repoPath}`);
        
        const runCmd = `docker rm -f ${containerName} || true && docker run -d --name ${containerName} --network ${networkName} -p ${port}:${port} ${imageName}`;
        await runBash(runCmd);

        console.log('✅ Docker container build + run success! Visit 👉 http://localhost:' + port);
        return true;
    } catch (error) {
        handleError(error, 'Error - solutionInstall');
    }
}

const installWithProgress = async (req, res) => {
    try {
        const repoUrl = 'https://github.com/devweam-ai/ai-doc-editor.git';
        const repoName = 'ai-doc-editor';
        const repoPath = `/workspace/${repoName}`;
        const imageName = 'ai-doc-editor-img';
        const containerName = 'ai-doc-editor-container';
        const networkName = 'weamai_app-network';
        const port = '3002';
        const branchName = 'mongodb';

        // Step 1: Clean up existing repository
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '🧹 Cleaning up existing repository...',
            step: 1,
            totalSteps: 5
        })}\n\n`);
        
        await runBashWithProgress(`rm -rf ${repoPath}`, res, 'Repository cleanup completed');

        // Step 2: Clone repository
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '📥 Cloning repository from GitHub...',
            step: 2,
            totalSteps: 5
        })}\n\n`);
        
        await runBashWithProgress(`git clone -b ${branchName} ${repoUrl} ${repoPath}`, res, 'Repository cloned successfully');

        // Step 3: Setup environment
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '⚙️ Setting up environment configuration...',
            step: 3,
            totalSteps: 5
        })}\n\n`);
        
        await runBashWithProgress(`cp ${repoPath}/env.example ${repoPath}/.env`, res, 'Environment configuration completed');

        // Step 4: Build Docker image
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '🐳 Building Docker image (this may take several minutes)...',
            step: 4,
            totalSteps: 5
        })}\n\n`);
        
        await runBashWithProgress(`docker build -t ${imageName} ${repoPath}`, res, 'Docker image built successfully');

        // Step 5: Run container
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '🚀 Starting Docker container...',
            step: 5,
            totalSteps: 5
        })}\n\n`);
        
        const runCmd = `docker rm -f ${containerName} || true && docker run -d --name ${containerName} --network ${networkName} -p ${port}:${port} ${imageName}`;
        await runBashWithProgress(runCmd, res, 'Container started successfully');

        // Final success message
        res.write(`data: ${JSON.stringify({ 
            type: 'success', 
            message: `✅ Installation completed successfully! Your solution is now running at http://localhost:${port}`,
            url: `http://localhost:${port}`,
            step: 5,
            totalSteps: 5
        })}\n\n`);

        console.log('✅ Docker container build + run success! Visit 👉 http://localhost:' + port);
        return true;
    } catch (error) {
        res.write(`data: ${JSON.stringify({ 
            type: 'error', 
            message: `❌ Installation failed: ${error.message}`,
            error: error.message
        })}\n\n`);
        handleError(error, 'Error - solutionInstallWithProgress');
        throw error;
    }
}

module.exports = {
    install,
    installWithProgress,
}