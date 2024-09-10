import tkinter as tk
from tkinter import messagebox, ttk
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import date

# Configuração do SQLAlchemy
Base = declarative_base()

# Tabela de associação entre Livro e Leitor (muitos-para-muitos) para empréstimos
livro_leitor = Table('livro_leitor', Base.metadata,
    Column('livro_id', Integer, ForeignKey('livros.id')),
    Column('leitor_id', Integer, ForeignKey('leitores.id')),
    Column('data_emprestimo', Date, default=date.today())
)

# Definição das Entidades
class Livro(Base):
    __tablename__ = 'livros'
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    autor_id = Column(Integer, ForeignKey('autores.id'))
    genero_id = Column(Integer, ForeignKey('generos.id'))

    autor = relationship("Autor", back_populates="livros")
    genero = relationship("Genero", back_populates="livros")
    leitores = relationship("Leitor", secondary=livro_leitor, back_populates="livros")

class Autor(Base):
    __tablename__ = 'autores'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    biografia = Column(String)
    livros = relationship("Livro", back_populates="autor")

class Genero(Base):
    __tablename__ = 'generos'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)
    livros = relationship("Livro", back_populates="genero")

class Leitor(Base):
    __tablename__ = 'leitores'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    livros = relationship("Livro", secondary=livro_leitor, back_populates="leitores")

# Configuração do banco de dados SQLite
engine = create_engine('sqlite:///biblioteca.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Funções CRUD
def adicionar_livro(titulo, isbn, autor_id, genero_id):
    novo_livro = Livro(titulo=titulo, isbn=isbn, autor_id=autor_id, genero_id=genero_id)
    session.add(novo_livro)
    session.commit()

def listar_livros():
    return session.query(Livro).all()

def adicionar_autor(nome, biografia):
    novo_autor = Autor(nome=nome, biografia=biografia)
    session.add(novo_autor)
    session.commit()

def listar_autores():
    return session.query(Autor).all()

def adicionar_genero(nome):
    novo_genero = Genero(nome=nome)
    session.add(novo_genero)
    session.commit()

def listar_generos():
    return session.query(Genero).all()

def adicionar_leitor(nome, email):
    novo_leitor = Leitor(nome=nome, email=email)
    session.add(novo_leitor)
    session.commit()

def listar_leitores():
    return session.query(Leitor).all()

def registrar_emprestimo(livro_id, leitor_id):
    leitor = session.query(Leitor).get(leitor_id)
    livro = session.query(Livro).get(livro_id)
    if livro and leitor:
        leitor.livros.append(livro)
        session.commit()

def listar_emprestimos():
    return session.query(Leitor).all()



def abrir_janela_livros():
    livro_window = tk.Toplevel()
    livro_window.title("Gerenciar Livros")

    def atualizar_lista_livros():
        livros = listar_livros()
        lista_livros.delete(*lista_livros.get_children())
        for livro in livros:
            autor = livro.autor.nome if livro.autor else "Desconhecido"
            genero = livro.genero.nome if livro.genero else "Desconhecido"
            lista_livros.insert("", "end", values=(livro.id, livro.titulo, livro.isbn, autor, genero))

    def salvar_livro():
        titulo = entry_titulo.get()
        isbn = entry_isbn.get()
        autor_id = combo_autor.get().split('-')[0].strip()  # Pegando o ID do autor
        genero_id = combo_genero.get().split('-')[0].strip()  # Pegando o ID do gênero
        if titulo and isbn and autor_id and genero_id:
            adicionar_livro(titulo, isbn, autor_id, genero_id)
            messagebox.showinfo("Sucesso", "Livro adicionado com sucesso!")
            atualizar_lista_livros()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

    def remover_livro():
        selected_item = lista_livros.selection()
        if selected_item:
            livro_id = lista_livros.item(selected_item, 'values')[0]
            session.query(Livro).filter_by(id=livro_id).delete()
            session.commit()
            messagebox.showinfo("Sucesso", "Livro removido com sucesso!")
            atualizar_lista_livros()
        else:
            messagebox.showerror("Erro", "Selecione um livro para remover.")

    def atualizar_livro():
        selected_item = lista_livros.selection()
        if selected_item:
            livro_id = lista_livros.item(selected_item, 'values')[0]
            novo_titulo = entry_titulo.get()
            novo_isbn = entry_isbn.get()
            autor_id = combo_autor.get().split('-')[0].strip()
            genero_id = combo_genero.get().split('-')[0].strip()

            livro = session.query(Livro).get(livro_id)
            if livro and novo_titulo and novo_isbn and autor_id and genero_id:
                livro.titulo = novo_titulo
                livro.isbn = novo_isbn
                livro.autor_id = autor_id
                livro.genero_id = genero_id
                session.commit()
                messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")
                atualizar_lista_livros()
            else:
                messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        else:
            messagebox.showerror("Erro", "Selecione um livro para atualizar.")

    # Layout da janela de livros
    tk.Label(livro_window, text="Título do Livro").grid(row=0, column=0)
    tk.Label(livro_window, text="ISBN do Livro").grid(row=1, column=0)
    tk.Label(livro_window, text="Autor").grid(row=2, column=0)
    tk.Label(livro_window, text="Gênero").grid(row=3, column=0)

    entry_titulo = tk.Entry(livro_window)
    entry_titulo.grid(row=0, column=1)

    entry_isbn = tk.Entry(livro_window)
    entry_isbn.grid(row=1, column=1)

    autores = listar_autores()
    autores_nomes = [f"{autor.id} - {autor.nome}" for autor in autores]
    combo_autor = ttk.Combobox(livro_window, values=autores_nomes)
    combo_autor.grid(row=2, column=1)

    generos = listar_generos()
    generos_nomes = [f"{genero.id} - {genero.nome}" for genero in generos]
    combo_genero = ttk.Combobox(livro_window, values=generos_nomes)
    combo_genero.grid(row=3, column=1)

    botao_adicionar_livro = tk.Button(livro_window, text="Adicionar Livro", command=salvar_livro)
    botao_adicionar_livro.grid(row=4, column=0, columnspan=2)

    botao_remover_livro = tk.Button(livro_window, text="Remover Livro", command=remover_livro)
    botao_remover_livro.grid(row=5, column=0)

    botao_atualizar_livro = tk.Button(livro_window, text="Atualizar Livro", command=atualizar_livro)
    botao_atualizar_livro.grid(row=5, column=1)

    lista_livros = ttk.Treeview(livro_window, columns=('ID', 'Título', 'ISBN', 'Autor', 'Gênero'), show='headings')
    lista_livros.heading('ID', text="ID")
    lista_livros.heading('Título', text="Título")
    lista_livros.heading('ISBN', text="ISBN")
    lista_livros.heading('Autor', text="Autor")
    lista_livros.heading('Gênero', text="Gênero")
    lista_livros.grid(row=6, column=0, columnspan=2)

    atualizar_lista_livros()


def abrir_janela_autores():
    autor_window = tk.Toplevel()
    autor_window.title("Gerenciar Autores")

    def atualizar_lista_autores():
        autores = listar_autores()
        lista_autores.delete(*lista_autores.get_children())
        for autor in autores:
            lista_autores.insert("", "end", values=(autor.id, autor.nome, autor.biografia))

    def salvar_autor():
        nome = entry_nome_autor.get()
        biografia = entry_biografia_autor.get()
        if nome:
            adicionar_autor(nome, biografia)
            messagebox.showinfo("Sucesso", "Autor adicionado com sucesso!")
            atualizar_lista_autores()
        else:
            messagebox.showerror("Erro", "Por favor, preencha o nome do autor.")

    def remover_autor():
        selected_item = lista_autores.selection()
        if selected_item:
            autor_id = lista_autores.item(selected_item, 'values')[0]
            session.query(Autor).filter_by(id=autor_id).delete()
            session.commit()
            messagebox.showinfo("Sucesso", "Autor removido com sucesso!")
            atualizar_lista_autores()
        else:
            messagebox.showerror("Erro", "Selecione um autor para remover.")

    def atualizar_autor():
        selected_item = lista_autores.selection()
        if selected_item:
            autor_id = lista_autores.item(selected_item, 'values')[0]
            nome = entry_nome_autor.get()
            biografia = entry_biografia_autor.get()

            autor = session.query(Autor).get(autor_id)
            if autor and nome:
                autor.nome = nome
                autor.biografia = biografia
                session.commit()
                messagebox.showinfo("Sucesso", "Autor atualizado com sucesso!")
                atualizar_lista_autores()
            else:
                messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        else:
            messagebox.showerror("Erro", "Selecione um autor para atualizar.")

    # Layout da janela de autores
    tk.Label(autor_window, text="Nome do Autor").grid(row=0, column=0)
    tk.Label(autor_window, text="Biografia").grid(row=1, column=0)

    entry_nome_autor = tk.Entry(autor_window)
    entry_nome_autor.grid(row=0, column=1)

    entry_biografia_autor = tk.Entry(autor_window)
    entry_biografia_autor.grid(row=1, column=1)

    botao_adicionar_autor = tk.Button(autor_window, text="Adicionar Autor", command=salvar_autor)
    botao_adicionar_autor.grid(row=2, column=0, columnspan=2)

    botao_remover_autor = tk.Button(autor_window, text="Remover Autor", command=remover_autor)
    botao_remover_autor.grid(row=3, column=0)

    botao_atualizar_autor = tk.Button(autor_window, text="Atualizar Autor", command=atualizar_autor)
    botao_atualizar_autor.grid(row=3, column=1)

    lista_autores = ttk.Treeview(autor_window, columns=('ID', 'Nome', 'Biografia'), show='headings')
    lista_autores.heading('ID', text="ID")
    lista_autores.heading('Nome', text="Nome")
    lista_autores.heading('Biografia', text="Biografia")
    lista_autores.grid(row=4, column=0, columnspan=2)

    atualizar_lista_autores()


def abrir_janela_generos():
    genero_window = tk.Toplevel()
    genero_window.title("Gerenciar Gêneros")

    def atualizar_lista_generos():
        generos = listar_generos()
        lista_generos.delete(*lista_generos.get_children())
        for genero in generos:
            lista_generos.insert("", "end", values=(genero.id, genero.nome))

    def salvar_genero():
        nome = entry_nome_genero.get()
        if nome:
            adicionar_genero(nome)
            messagebox.showinfo("Sucesso", "Gênero adicionado com sucesso!")
            atualizar_lista_generos()
        else:
            messagebox.showerror("Erro", "Por favor, preencha o nome do gênero.")

    def remover_genero():
        selected_item = lista_generos.selection()
        if selected_item:
            genero_id = lista_generos.item(selected_item, 'values')[0]
            session.query(Genero).filter_by(id=genero_id).delete()
            session.commit()
            messagebox.showinfo("Sucesso", "Gênero removido com sucesso!")
            atualizar_lista_generos()
        else:
            messagebox.showerror("Erro", "Selecione um gênero para remover.")

    def atualizar_genero():
        selected_item = lista_generos.selection()
        if selected_item:
            genero_id = lista_generos.item(selected_item, 'values')[0]
            nome = entry_nome_genero.get()

            genero = session.query(Genero).get(genero_id)
            if genero and nome:
                genero.nome = nome
                session.commit()
                messagebox.showinfo("Sucesso", "Gênero atualizado com sucesso!")
                atualizar_lista_generos()
            else:
                messagebox.showerror("Erro", "Preencha o nome corretamente.")
        else:
            messagebox.showerror("Erro", "Selecione um gênero para atualizar.")

    # Layout da janela de gêneros
    tk.Label(genero_window, text="Nome do Gênero").grid(row=0, column=0)

    entry_nome_genero = tk.Entry(genero_window)
    entry_nome_genero.grid(row=0, column=1)

    botao_adicionar_genero = tk.Button(genero_window, text="Adicionar Gênero", command=salvar_genero)
    botao_adicionar_genero.grid(row=1, column=0, columnspan=2)

    botao_remover_genero = tk.Button(genero_window, text="Remover Gênero", command=remover_genero)
    botao_remover_genero.grid(row=2, column=0)

    botao_atualizar_genero = tk.Button(genero_window, text="Atualizar Gênero", command=atualizar_genero)
    botao_atualizar_genero.grid(row=2, column=1)

    lista_generos = ttk.Treeview(genero_window, columns=('ID', 'Nome'), show='headings')
    lista_generos.heading('ID', text="ID")
    lista_generos.heading('Nome', text="Nome")
    lista_generos.grid(row=3, column=0, columnspan=2)

    atualizar_lista_generos()


def abrir_janela_emprestimos():
    emprestimo_window = tk.Toplevel()
    emprestimo_window.title("Gerenciar Empréstimos")

    def atualizar_lista_emprestimos():
        leitores = listar_emprestimos()
        lista_emprestimos.delete(*lista_emprestimos.get_children())
        for leitor in leitores:
            livros = ", ".join([livro.titulo for livro in leitor.livros])
            lista_emprestimos.insert("", "end", values=(leitor.id, leitor.nome, livros))

    def registrar():
        leitor_id = combo_leitor.get().split('-')[0].strip()  # Pegando o ID do leitor
        livro_id = combo_livro.get().split('-')[0].strip()  # Pegando o ID do livro
        if leitor_id and livro_id:
            registrar_emprestimo(livro_id, leitor_id)
            messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!")
            atualizar_lista_emprestimos()
        else:
            messagebox.showerror("Erro", "Por favor, selecione um leitor e um livro.")

    def remover_emprestimo():
        selected_item = lista_emprestimos.selection()
        if selected_item:
            leitor_id = lista_emprestimos.item(selected_item, 'values')[0]
            livro_nome = lista_emprestimos.item(selected_item, 'values')[2].split(",")[0]  # Pegando o nome do primeiro livro
            livro = session.query(Livro).filter_by(titulo=livro_nome).first()

            leitor = session.query(Leitor).get(leitor_id)
            if livro in leitor.livros:
                leitor.livros.remove(livro)
                session.commit()
                messagebox.showinfo("Sucesso", "Empréstimo removido com sucesso!")
                atualizar_lista_emprestimos()
            else:
                messagebox.showerror("Erro", "Erro ao remover o empréstimo.")
        else:
            messagebox.showerror("Erro", "Selecione um empréstimo para remover.")

    def atualizar_emprestimo():
        selected_item = lista_emprestimos.selection()
        if selected_item:
            leitor_id_atual = lista_emprestimos.item(selected_item, 'values')[0]
            livro_nome = lista_emprestimos.item(selected_item, 'values')[2].split(",")[0]
            livro = session.query(Livro).filter_by(titulo=livro_nome).first()

            novo_leitor_id = combo_leitor.get().split('-')[0].strip()
            if novo_leitor_id and livro:
                leitor_atual = session.query(Leitor).get(leitor_id_atual)
                novo_leitor = session.query(Leitor).get(novo_leitor_id)

                # Remover o livro do leitor atual e adicionar ao novo leitor
                if livro in leitor_atual.livros:
                    leitor_atual.livros.remove(livro)
                    novo_leitor.livros.append(livro)
                    session.commit()
                    messagebox.showinfo("Sucesso", "Empréstimo atualizado com sucesso!")
                    atualizar_lista_emprestimos()
                else:
                    messagebox.showerror("Erro", "Erro ao atualizar o empréstimo.")
            else:
                messagebox.showerror("Erro", "Selecione um novo leitor e um livro para atualizar o empréstimo.")
        else:
            messagebox.showerror("Erro", "Selecione um empréstimo para atualizar.")

    # Layout da janela de empréstimos
    tk.Label(emprestimo_window, text="Leitor").grid(row=0, column=0)
    tk.Label(emprestimo_window, text="Livro").grid(row=1, column=0)

    leitores = listar_leitores()
    leitores_nomes = [f"{leitor.id} - {leitor.nome}" for leitor in leitores]
    combo_leitor = ttk.Combobox(emprestimo_window, values=leitores_nomes)
    combo_leitor.grid(row=0, column=1)

    livros = listar_livros()
    livros_nomes = [f"{livro.id} - {livro.titulo}" for livro in livros]
    combo_livro = ttk.Combobox(emprestimo_window, values=livros_nomes)
    combo_livro.grid(row=1, column=1)

    botao_registrar = tk.Button(emprestimo_window, text="Registrar Empréstimo", command=registrar)
    botao_registrar.grid(row=2, column=0, columnspan=2)

    botao_remover_emprestimo = tk.Button(emprestimo_window, text="Remover Empréstimo", command=remover_emprestimo)
    botao_remover_emprestimo.grid(row=3, column=0)

    botao_atualizar_emprestimo = tk.Button(emprestimo_window, text="Atualizar Empréstimo", command=atualizar_emprestimo)
    botao_atualizar_emprestimo.grid(row=3, column=1)

    lista_emprestimos = ttk.Treeview(emprestimo_window, columns=('LeitorID', 'LeitorNome', 'Livros'), show='headings')
    lista_emprestimos.heading('LeitorID', text="ID do Leitor")
    lista_emprestimos.heading('LeitorNome', text="Nome do Leitor")
    lista_emprestimos.heading('Livros', text="Livros Emprestados")
    lista_emprestimos.grid(row=4, column=0, columnspan=2)

    atualizar_lista_emprestimos()


def abrir_janela_leitores():
    leitor_window = tk.Toplevel()
    leitor_window.title("Gerenciar Leitores")

    def atualizar_lista_leitores():
        leitores = listar_leitores()
        lista_leitores.delete(*lista_leitores.get_children())
        for leitor in leitores:
            lista_leitores.insert("", "end", values=(leitor.id, leitor.nome, leitor.email))

    def salvar_leitor():
        nome = entry_nome_leitor.get()
        email = entry_email_leitor.get()
        if nome and email:
            adicionar_leitor(nome, email)
            messagebox.showinfo("Sucesso", "Leitor adicionado com sucesso!")
            atualizar_lista_leitores()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

    def remover_leitor():
        selected_item = lista_leitores.selection()
        if selected_item:
            leitor_id = lista_leitores.item(selected_item, 'values')[0]
            session.query(Leitor).filter_by(id=leitor_id).delete()
            session.commit()
            messagebox.showinfo("Sucesso", "Leitor removido com sucesso!")
            atualizar_lista_leitores()
        else:
            messagebox.showerror("Erro", "Selecione um leitor para remover.")

    def atualizar_leitor():
        selected_item = lista_leitores.selection()
        if selected_item:
            leitor_id = lista_leitores.item(selected_item, 'values')[0]
            nome = entry_nome_leitor.get()
            email = entry_email_leitor.get()

            leitor = session.query(Leitor).get(leitor_id)
            if leitor and nome and email:
                leitor.nome = nome
                leitor.email = email
                session.commit()
                messagebox.showinfo("Sucesso", "Leitor atualizado com sucesso!")
                atualizar_lista_leitores()
            else:
                messagebox.showerror("Erro", "Preencha todos os campos corretamente.")
        else:
            messagebox.showerror("Erro", "Selecione um leitor para atualizar.")

    # Layout da janela de leitores
    tk.Label(leitor_window, text="Nome do Leitor").grid(row=0, column=0)
    tk.Label(leitor_window, text="Email").grid(row=1, column=0)

    entry_nome_leitor = tk.Entry(leitor_window)
    entry_nome_leitor.grid(row=0, column=1)

    entry_email_leitor = tk.Entry(leitor_window)
    entry_email_leitor.grid(row=1, column=1)

    botao_adicionar_leitor = tk.Button(leitor_window, text="Adicionar Leitor", command=salvar_leitor)
    botao_adicionar_leitor.grid(row=2, column=0, columnspan=2)

    botao_remover_leitor = tk.Button(leitor_window, text="Remover Leitor", command=remover_leitor)
    botao_remover_leitor.grid(row=3, column=0)

    botao_atualizar_leitor = tk.Button(leitor_window, text="Atualizar Leitor", command=atualizar_leitor)
    botao_atualizar_leitor.grid(row=3, column=1)

    lista_leitores = ttk.Treeview(leitor_window, columns=('ID', 'Nome', 'Email'), show='headings')
    lista_leitores.heading('ID', text="ID")
    lista_leitores.heading('Nome', text="Nome")
    lista_leitores.heading('Email', text="Email")
    lista_leitores.grid(row=4, column=0, columnspan=2)

    atualizar_lista_leitores()


# Interface principal de Tkinter
root = tk.Tk()
root.title("Sistema de Biblioteca")

# Botões principais para abrir as janelas de gerenciamento
botao_gerenciar_livros = tk.Button(root, text="Gerenciar Livros", command=abrir_janela_livros)
botao_gerenciar_livros.grid(row=0, column=0)

botao_gerenciar_autores = tk.Button(root, text="Gerenciar Autores", command=abrir_janela_autores)
botao_gerenciar_autores.grid(row=1, column=0)

botao_gerenciar_generos = tk.Button(root, text="Gerenciar Gêneros", command=abrir_janela_generos)
botao_gerenciar_generos.grid(row=2, column=0)

botao_gerenciar_leitores = tk.Button(root, text="Gerenciar Leitores", command=abrir_janela_leitores)
botao_gerenciar_leitores.grid(row=3, column=0)

botao_registrar_emprestimo = tk.Button(root, text="Registrar Empréstimos", command=abrir_janela_emprestimos)
botao_registrar_emprestimo.grid(row=4, column=0)

# Iniciar o loop da interface
root.mainloop()
