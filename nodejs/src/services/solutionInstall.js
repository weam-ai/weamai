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

// Solution configurations
const SOLUTION_CONFIGS = {
    'ai-doc-editor': {
        repoUrl: 'https://github.com/devweam-ai/ai-doc-editor.git',
        repoName: 'ai-doc-editor',
        imageName: 'ai-doc-editor-img',
        containerName: 'ai-doc-editor-container',
        port: '3002',
        branchName: 'development',
        installType: 'docker', // docker or docker-compose
        envFile: 'env.example'
    },
    'seo-content-gen': {
        repoUrl: 'https://github.com/devweam-ai/seo-content-gen.git',
        repoName: 'seo-content-gen',
        imageName: 'seo-content-gen-img',
        containerName: 'seo-content-gen-container',
        port: '3003',
        branchName: 'opensource-deployment',
        installType: 'docker-compose', // docker or docker-compose
        envFile: null, // No env file needed for docker-compose
        // Additional ports that might be used by docker-compose
        additionalPorts: ['9001', '9002', '9003']
    }
};

// Removed install() function - using only installWithProgress() to avoid double execution

const installWithProgress = async (req, res) => {
    try {
        // Get solution type from request body or default to ai-doc-editor
        const solutionType = req.body?.solutionType || 'ai-doc-editor';
        const config = SOLUTION_CONFIGS[solutionType];
        
        if (!config) {
            throw new Error(`Unknown solution type: ${solutionType}`);
        }

        const repoPath = `/workspace/${config.repoName}`;
        const networkName = 'weamai_app-network';
        const totalSteps = config.installType === 'docker' ? 5 : 5;

        // Step 1: Clean up existing repository
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '🧹 Cleaning up existing repository...',
            step: 1,
            totalSteps: totalSteps
        })}\n\n`);
        
        await runBashWithProgress(`rm -rf ${repoPath}`, res, 'Repository cleanup completed');

        // Step 2: Clone repository
        res.write(`data: ${JSON.stringify({ 
            type: 'progress', 
            message: '📥 Cloning repository from GitHub...',
            step: 2,
            totalSteps: totalSteps
        })}\n\n`);
        
        await runBashWithProgress(`git clone -b ${config.branchName} ${config.repoUrl} ${repoPath}`, res, 'Repository cloned successfully');

        if (config.installType === 'docker') {
            // Step 3: Setup environment (Docker only)
            res.write(`data: ${JSON.stringify({ 
                type: 'progress', 
                message: '⚙️ Setting up environment configuration...',
                step: 3,
                totalSteps: totalSteps
            })}\n\n`);
            
            await runBashWithProgress(`cp ${repoPath}/${config.envFile} ${repoPath}/.env`, res, 'Environment configuration completed');

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
                totalSteps: totalSteps
            })}\n\n`);
            
            const buildCmd = `docker build -t ${config.imageName} ${buildArgs} ${repoPath}`;
            await runBashWithProgress(buildCmd, res, 'Docker image built successfully');

            // Step 5: Run container
            res.write(`data: ${JSON.stringify({ 
                type: 'progress', 
                message: '🚀 Starting Docker container...',
                step: 5,
                totalSteps: totalSteps
            })}\n\n`);
            
            const runCmd = `docker rm -f ${config.containerName} || true && docker run -d --name ${config.containerName} --network ${networkName} -p ${config.port}:${config.port} ${config.imageName}`;
            await runBashWithProgress(runCmd, res, 'Container started successfully');

        } else if (config.installType === 'docker-compose') {
            // Step 3: Setup environment files
            res.write(`data: ${JSON.stringify({ 
                type: 'progress', 
                message: '⚙️ Setting up environment configuration files...',
                step: 3,
                totalSteps: totalSteps
            })}\n\n`);
            
            await runBashWithProgress(`find ${repoPath} -name ".env.example" -exec sh -c 'cp "$1" "$(dirname "$1")/.env"' _ {} \\;`, res, 'Environment files setup completed');

            // Step 4: Install docker-compose if needed
            res.write(`data: ${JSON.stringify({ 
                type: 'progress', 
                message: '📦 Installing Docker Compose if needed...',
                step: 4,
                totalSteps: totalSteps
            })}\n\n`);
            
            try {
                await runBashWithProgress(`which docker-compose || (wget -O /usr/local/bin/docker-compose "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" && chmod +x /usr/local/bin/docker-compose)`, res, 'Docker Compose installation completed');

                // Step 5: Build and run with docker-compose
                res.write(`data: ${JSON.stringify({ 
                    type: 'progress', 
                    message: '🐳 Building and starting services with Docker Compose...',
                    step: 5,
                    totalSteps: totalSteps
                })}\n\n`);
                
                // First, stop any existing containers that might be using the ports
                await runBashWithProgress(`cd ${repoPath} && docker-compose down`, res, 'Stopped existing containers');
                
                // Check and free up ports that might be in use
                if (config.additionalPorts) {
                    for (const port of config.additionalPorts) {
                        await runBashWithProgress(`docker ps -q --filter "publish=${port}" | xargs -r docker stop`, res, `Freed up port ${port}`);
                    }
                }
                
                // Now try to start the services
                const composeCmd = `cd ${repoPath} && docker-compose up -d --build`;
                await runBashWithProgress(composeCmd, res, 'Docker Compose services started successfully');
            } catch (error) {
                res.write(`data: ${JSON.stringify({ 
                    type: 'progress', 
                    message: '⚠️ Docker Compose failed, trying alternative approach...',
                    step: 5,
                    totalSteps: totalSteps
                })}\n\n`);
                
                // Fallback: try to find and build individual services
                res.write(`data: ${JSON.stringify({ 
                    type: 'output', 
                    message: '🔍 Looking for individual Dockerfiles in subdirectories...',
                    timestamp: new Date().toISOString()
                })}\n\n`);
                
                // Look for Dockerfiles in subdirectories (frontend, node, python)
                await runBashWithProgress(`cd ${repoPath} && find . -name "Dockerfile" -type f`, res, 'Found Dockerfiles');
                
                // Try to build the main service (usually frontend or the one with the main Dockerfile)
                await runBashWithProgress(`cd ${repoPath}/frontend && if [ -f Dockerfile ]; then docker build -t ${config.imageName} .; else echo "No Dockerfile in frontend"; fi`, res, 'Frontend Docker image built');
                
                // Run the container
                await runBashWithProgress(`docker run -d --name ${config.containerName} --network ${networkName} -p ${config.port}:${config.port} ${config.imageName}`, res, 'Container started successfully');
            }
        }

        // Final success message
        res.write(`data: ${JSON.stringify({ 
            type: 'success', 
            message: `✅ Installation completed successfully! Your ${config.repoName} solution is now running at http://localhost:${config.port}`,
            url: `http://localhost:${config.port}`,
            step: totalSteps,
            totalSteps: totalSteps,
            solutionType: solutionType
        })}\n\n`);

        console.log('✅ Solution installation success! Visit 👉 http://localhost:' + config.port);
        return { success: true, port: config.port, solutionType };
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
    installWithProgress,
}