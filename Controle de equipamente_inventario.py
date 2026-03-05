import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3


# ----BANCO DE DADOS ----#
def conectar():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos
                      (
                          id
                          INTEGER
                          PRIMARY
                          KEY
                          AUTOINCREMENT,
                          patrimonio
                          TEXT
                          UNIQUE,
                          nome
                          TEXT,
                          setor
                          TEXT,
                          responsa
                          TEXT
                      )''')
    conn.commit()
    return conn


# -- FUNÇÕES DE LÓGICA --#
def salvar_produto():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO produtos (patrimonio, nome, setor, responsa) VALUES (?, ?, ?, ?)",
                       (entry_pat.get(), entry_nome.get(), entry_setor.get(), entry_resp.get()))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto cadastrado!")
        exibir_inventario()
        limpar_campos()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Este número patrimonial já existe!")
    finally:
        conn.close()


def exibir_inventario():
    for i in tabela.get_children():
        tabela.delete(i)
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    for linha in cursor.fetchall():
        tabela.insert("", tk.END, values=linha)
    conn.close()


def consultar_produto():
    pat = entry_pat.get()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE patrimonio = ?", (pat,))
    produto = cursor.fetchone()
    conn.close()

    if produto:
        limpar_campos()
        # Índices: 0=ID, 1=Pat, 2=Nome, 3=Setor, 4=Resp
        entry_pat.insert(0, produto[1])
        entry_nome.insert(0, produto[2])
        entry_setor.insert(0, produto[3])
        entry_resp.insert(0, produto[4])
    else:
        messagebox.showinfo("Busca", "Nenhum produto encontrado.")


def excluir_produto():
    pat = entry_pat.get()
    if not pat: return
    if messagebox.askyesno("Confirmar", f"Excluir item {pat}?"):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE patrimonio = ?", (pat,))
        conn.commit()
        conn.close()
        exibir_inventario()
        limpar_campos()


def limpar_campos():
    entry_pat.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_setor.delete(0, tk.END)
    entry_resp.delete(0, tk.END)


# Função para preencher campos ao clicar na tabela
def preencher_campos(event):
    item_selecionado = tabela.selection()
    if item_selecionado:
        # Pega os dados da linha clicada
        valores = tabela.item(item_selecionado)['values']
        limpar_campos()
        entry_pat.insert(0, valores[1])
        entry_nome.insert(0, valores[2])
        entry_setor.insert(0, valores[3])
        entry_resp.insert(0, valores[4])

def editar_produto():
    pat = entry_pat.get()
    if not pat:
        messagebox.showwarning("Atenção", "Selecione um ítem ou digite o Nº Patrimonial para editar.")
        return

    if messagebox.askyesno("Confirmar", f"Deseja salvar as alterações no ítem {pat}?"):
        conn = conectar()
        cursor = conn.cursor()
        #Atualiza os dados onde o patrimônio for igual ao digitado
        cursor.execute("""UPDATE produtos
                          SET nome = ?, setor = ?, responsa = ?
                          WHERE patrimonio = ?""",
                       (entry_nome.get(), entry_setor.get(), entry_resp.get(), pat))
        conn.commit()
        if cursor.rowcount > 0:
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            exibir_inventario()
        else:
            messagebox.showerror("Erro", "Produto não encontrado para edição.")
        conn.close()
def filtrar_tabela(event):
    termo = entry_busca.get() # Pega o que você digitou na busca

    #Limpa a tabela par amostrar o filtro
    for i in tabela.get_children():
        tabela.delete(i)
    conn = conectar()
    cursor = conn.cursor()
    #Busca nomes que contenham o termo digitado (ignore maíusculas/minúsculas)
    cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", ('%' + termo + '%',))

    for linha in cursor.fetchall():
        tabela.insert("", tk.END, values=linha)
    conn.close()


# --- INTERFACE ---#
janela = tk.Tk()
janela.title("Gestão de Inventário")
janela.geometry("650x600")

# 1. Container de Inputs (usando apenas PACK)
frame_inputs = tk.Frame(janela)
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="Nº Patrimonial:").pack()
entry_pat = tk.Entry(frame_inputs, width=40)
entry_pat.pack(pady=2)

tk.Label(frame_inputs, text="Aparelho/Produto:").pack()
entry_nome = tk.Entry(frame_inputs, width=40)
entry_nome.pack(pady=2)

tk.Label(frame_inputs, text="Setor").pack()
entry_setor = tk.Entry(frame_inputs, width=40)
entry_setor.pack(pady=2)

tk.Label(frame_inputs, text="Responsável pelo ítem:").pack()
entry_resp = tk.Entry(frame_inputs, width=40)
entry_resp.pack(pady=2)

# 2. Container de Botões (usando apenas GRID dentro deste frame específico)
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="Salvar", command=salvar_produto, width=12, fg="blue").grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Editar", command=editar_produto, width=12, fg="orange").grid(row=0, column=1, padx=5, pady=5) # NOVO
tk.Button(frame_botoes, text="Consultar", command=consultar_produto, width=12).grid(row=0, column=2, padx=5, pady=5)

tk.Button(frame_botoes, text="Limpar", command=limpar_campos, width=12).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_botoes, text="Excluir", command=excluir_produto, width=12, fg="red").grid(row=1, column=1, padx=5,pady=5)

#---- BARAR DE PESQUISA ---#
frame_busca = tk.Frame(janela)
frame_busca.pack(pady=5)

tk.Label(frame_busca, text="🔍 Pesquisar por Nome:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
entry_busca = tk.Entry(frame_busca, width=30)
entry_busca.pack(side=tk.LEFT)

#O "Bind" que faz a busca funcionar em tempo real
entry_busca.bind("<KeyRelease>", filtrar_tabela)

# 3. Tabela
colunas = ("ID", "Patrimônio", "Nome", "Setor", "Responsável")
tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=8)

for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, width=100, anchor="center")

tabela.pack(pady=10, padx=10, fill=tk.BOTH)

# Bind para o clique na tabela
tabela.bind("<<TreeviewSelect>>", preencher_campos)

conectar()
exibir_inventario()
janela.mainloop()
