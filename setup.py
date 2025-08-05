#!/usr/bin/env python3
"""
Setup script para Dashboard Papello
Facilita a instalação e configuração inicial
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    print("🎯" * 20)
    print("   DASHBOARD PAPELLO - SETUP")
    print("🎯" * 20)
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - OK")

def install_requirements():
    """Instala dependências do requirements.txt"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        sys.exit(1)

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando estrutura de pastas...")
    
    directories = [
        ".streamlit",
        "logs",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")

def check_credentials():
    """Verifica se as credenciais Google estão configuradas"""
    print("\n🔑 Verificando credenciais Google...")
    
    if os.path.exists("papello-credentials.json"):
        try:
            with open("papello-credentials.json", "r") as f:
                creds = json.load(f)
                print(f"✅ Credenciais encontradas - Project: {creds.get('project_id', 'N/A')}")
        except:
            print("⚠️  Arquivo de credenciais existe mas pode estar corrompido")
    else:
        print("⚠️  Credenciais Google não encontradas")
        print("   📋 Para configurar:")
        print("   1. Acesse Google Cloud Console")
        print("   2. Crie Service Account")
        print("   3. Baixe JSON como 'papello-credentials.json'")

def create_config_file():
    """Cria arquivo de configuração do Streamlit"""
    config_dir = Path(".streamlit")
    config_file = config_dir / "config.toml"
    
    if not config_file.exists():
        print("\n⚙️  Criando configuração Streamlit...")
        config_content = '''[global]
developmentMode = false

[server]
runOnSave = true
port = 8501

[theme]
primaryColor = "#96CA00"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
'''
        with open(config_file, "w") as f:
            f.write(config_content)
        print("✅ Configuração criada")

def run_dashboard():
    """Executa o dashboard"""
    print("\n🚀 Iniciando dashboard...")
    print("   URL: http://localhost:8501")
    print("   Pressione Ctrl+C para parar")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dash3.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard interrompido pelo usuário")

def main():
    print_header()
    
    # Verificações
    check_python_version()
    
    # Setup
    install_requirements()
    create_directories()
    create_config_file()
    check_credentials()
    
    print("\n" + "=" * 50)
    print("✅ SETUP CONCLUÍDO!")
    print("=" * 50)
    
    # Opção de executar
    response = input("\n🚀 Deseja executar o dashboard agora? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        run_dashboard()
    else:
        print("\n📋 Para executar o dashboard:")
        print("   streamlit run dash3.py")
        print("\n📚 Documentação completa: README.md")

if __name__ == "__main__":
    main()