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

        // const repoUrl = 'https://github.com/dnp176/New-Pratima-Infotech.git';
        // const repoName = 'New-Pratima-Infotech';
        // const repoPath = `/workspace/${repoName}`; // host mapped folder (bind mount required)
        // const imageName = 'my-nginx-img';
        // const containerName = 'my-nginx-img-container';
        // const networkName = 'app-network'; // must exist (same as docker-compose network)

        const repoUrl = 'https://github.com/devweam-ai/ai-doc-editor.git';
        const repoName = 'ai-doc-editor';
        const repoPath = `/workspace/${repoName}`;
        const imageName = 'ai-doc-editor-img';
        const containerName = 'ai-doc-editor-container';
        const networkName = 'app-network';

        // Step 1: Clone development branch
        // await runBash(`rm -rf ${repoPath} && git clone -b development ${repoUrl} ${repoPath}`);

        // Step 1.5: Copy env.example → .env
        // await runBash(`cp ${repoPath}/env.example ${repoPath}/.env`);
        
        // Step 2: Docker build (development branch Dockerfile)
        await runBash(`docker build -t ${imageName} ${repoPath}`);
        
        // Step 3: Run container
        const runCmd = `docker rm -f ${containerName} || true && docker run -d --name ${containerName} --network ${networkName} -p 8080:80 ${imageName}`;
        await runBash(runCmd);

        console.log('✅ Docker container build + run success! Visit 👉 http://localhost:3002');
        return true;
    } catch (error) {
        handleError(error, 'Error - solutionInstall');
    }
}

module.exports = {
    install,
}