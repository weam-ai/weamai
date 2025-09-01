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

        await runBash(`docker build -t ${imageName} ${repoPath}`);
        
        const runCmd = `docker rm -f ${containerName} || true && docker run -d --name ${containerName} --network ${networkName} -p ${port}:${port} ${imageName}`;
        await runBash(runCmd);

        console.log('✅ Docker container build + run success! Visit 👉 http://localhost:' + port);
        return true;
    } catch (error) {
        handleError(error, 'Error - solutionInstall');
    }
}

module.exports = {
    install,
}