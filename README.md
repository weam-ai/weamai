Sure! Below is a **perfectly formatted Markdown guide** for setting up Docker and WSL 2 on **Windows**, running a `build.sh` script, and using `docker-compose`. It also includes proper VS Code settings for line endings.

---

# 🚀 Docker & WSL2 Setup on Windows + Running `build.sh` and `docker-compose`

Follow these steps to install Docker, set up WSL2 with Ubuntu, and run your development environment.

---

## ✅ 1. Install Docker Desktop for Windows

📥 **Download Docker Desktop**
[🔗 https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)

🔧 During installation:

* Enable **WSL 2** integration when prompted.
* Select your preferred Linux distro (e.g., **Ubuntu**).

---

## ✅ 2. Install WSL2 with Ubuntu

### 🖥️ In **PowerShell (Admin)**, run:

```powershell
wsl --install Ubuntu
```

🌀 This will:

* Enable WSL features
* Download and install **Ubuntu**
* Set Ubuntu as your default WSL distro

📌 After installation, **restart your computer** if required.

---

## ✅ 3. Open Ubuntu (WSL2 Terminal)

* Open **Start Menu → Ubuntu**
* Set a **username and password** when prompted

---

## ✅ 4. VS Code: Configure Line Endings to `LF`

In **Visual Studio Code**:

1. Open your project folder.
2. Look at the bottom-right corner for `CRLF`.
3. Click on it and select `LF` (Line Feed).

> ⚠️ Using `CRLF` (Windows line endings) in shell scripts can cause errors.

---

## ✅ 5. Make Sure Docker Is Running

* Start **Docker Desktop**
* Wait until it says **"Docker is running"**

---

## ✅ 6. Navigate to Your Project in WSL

Open the **Ubuntu terminal** (WSL) and run:

```bash
cd /mnt/c/Users/YOUR_USERNAME/path/to/your/project
```

Replace `YOUR_USERNAME` and path accordingly.

---

## ✅ 7. Run `build.sh`

### Make the script executable:

```bash
chmod +x build.sh
```

### Then run it:

```bash
bash build.sh
```

---

## ✅ 8. Copy `.env.example` to `.env`

```bash
cp .env.example .env
```

> 📝 Modify `.env` as needed for your project settings.

---

## ✅ 9. Run Docker Compose

```bash
docker-compose up --build
```

---

## ✅ Optional: Use VS Code with WSL

1. Install **[Remote - WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl)** extension
2. Open WSL folder in VS Code:

   * Open Command Palette (`Ctrl+Shift+P`)
   * Select `Remote-WSL: Open Folder in WSL...`

---

## ✅ You’re Done!

Your project should now be running in Docker using WSL2. If any errors occur, check:

* Docker logs
* `.env` configuration
* Permissions or line endings in `build.sh`

---

Let me know if you’d like this saved as a `.md` file or added to your project README!
