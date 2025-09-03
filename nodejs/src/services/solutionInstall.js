const { handleError } = require('../utils/helper');
const { spawn } = require('child_process');
const fs = require('fs');

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

// Function to merge environment variables and create build args
function mergeEnvAndCreateBuildArgs(rootEnvPath, localEnvPath) {
    try {
        // Read root .env file
        let rootEnvVars = {};
        if (fs.existsSync(rootEnvPath)) {
            const rootContent = fs.readFileSync(rootEnvPath, 'utf8');
            rootContent.split('\n').forEach(line => {
                const trimmedLine = line.trim();
                if (trimmedLine && !trimmedLine.startsWith('#') && trimmedLine.includes('=')) {
                    const [key, ...valueParts] = trimmedLine.split('=');
                    rootEnvVars[key.trim()] = valueParts.join('=').trim();
                }
            });
        }

        // Read local .env file
        let localEnvVars = {};
        if (fs.existsSync(localEnvPath)) {
            const localContent = fs.readFileSync(localEnvPath, 'utf8');
            localContent.split('\n').forEach(line => {
                const trimmedLine = line.trim();
                if (trimmedLine && !trimmedLine.startsWith('#') && trimmedLine.includes('=')) {
                    const [key, ...valueParts] = trimmedLine.split('=');
                    localEnvVars[key.trim()] = valueParts.join('=').trim();
                }
            });
        }

        // Merge: start with local, add missing from root
        const mergedEnvVars = { ...localEnvVars };
        Object.keys(rootEnvVars).forEach(varName => {
            if (rootEnvVars[varName] && !mergedEnvVars[varName]) {
                mergedEnvVars[varName] = rootEnvVars[varName];
            }
        });

        // Create Docker build args
        const buildArgs = [];
        Object.entries(mergedEnvVars).forEach(([key, value]) => {
            const escapedValue = value.replace(/"/g, '\\"');
            buildArgs.push(`--build-arg ${key}="${escapedValue}"`);
        });

        console.log(`✅ Merged ${Object.keys(mergedEnvVars).length} environment variables`);
        return buildArgs.join(' ');
    } catch (error) {
        console.error('❌ Error merging environment files:', error);
        throw error;
    }
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
        
        // Merge environment variables and create build args
        const rootEnvPath = '/workspace/.env';
        const localEnvPath = `${repoPath}/.env`;
        const buildArgs = mergeEnvAndCreateBuildArgs(rootEnvPath, localEnvPath);
        
        // Build Docker image with environment variables as build args
        const buildCmd = `docker build -t ${imageName} ${buildArgs} ${repoPath}`;
        await runBash(buildCmd);
        
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

        // Merge environment variables and create build args
        const rootEnvPath = '/workspace/.env';
        const localEnvPath = `${repoPath}/.env`;
        const buildArgs = mergeEnvAndCreateBuildArgs(rootEnvPath, localEnvPath);
        
        res.write(`data: ${JSON.stringify({ 
            type: 'output', 
            message: `✅ Environment variables merged: ${buildArgs.split('--build-arg').length - 1} variables`,
            timestamp: new Date().toISOString()
        })}\n\n`);

        // Step 4: Build Docker image
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '🐳 Building Docker image (this may take several minutes)...',
            step: 4,
            totalSteps: 5
        })}\n\n`);
        
        const buildCmd = `docker build -t ${imageName} ${buildArgs} ${repoPath}`;
        await runBashWithProgress(buildCmd, res, 'Docker image built successfully');

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