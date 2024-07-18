import tkinter as tk
from tkinter import scrolledtext

def iniciar_script():
    console_text.insert(tk.END, "Script iniciado!\n")
    # Aqui você pode adicionar o código que deseja executar ao iniciar o script

def reiniciar_script():
    console_text.insert(tk.END, "Script reiniciado!\n")
    # Aqui você pode adicionar o código que deseja executar ao reiniciar o script

# Criar a janela principal
root = tk.Tk()
root.title("ZHsolution")
root.geometry("800x400")
root.configure(bg="#041232")  # Definir a cor de fundo da janela

# Configurar a grade para posicionamento dos widgets
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=8)

# Criar botão de iniciar
botao_iniciar = tk.Button(root, text="Iniciar", command=iniciar_script, font=("Helvetica", 12))
botao_iniciar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Criar botão de reiniciar
botao_reiniciar = tk.Button(root, text="Reiniciar", command=reiniciar_script, font=("Helvetica", 12))
botao_reiniciar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Criar área de texto para o console
console_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=("Helvetica", 14), bg="white")
console_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Iniciar o loop principal da interface gráfica
root.mainloop()
