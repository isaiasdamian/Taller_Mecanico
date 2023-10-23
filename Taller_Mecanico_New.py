import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import re

rol_actual = None
nuevo_usuario = None
nueva_password = None
nuevo_rol = None
nombre_usuario = None
apellido_paterno = None
apellido_materno = None
telefono = None
direccion = None
modo_formulario = "nuevo"
modo_formulario_clientes = "nuevo"
modo_formulario_vehiculos = "nuevo"
modo_formulario_piezas = "nuevo"
modo_formulario_reparaciones = "nuevo"
user_logged_in_id = None
id_usuario_combobox = None
id_cliente_combobox = None
id_vehiculo_combobox = None
id_pieza_combobox = None
id_mecanico_combobox = None
vista_general_combobox = None
vista_general_m_combobox = None
vista_general_s_combobox = None

#Matricula unica  LISTO
#CRUD de las otras pestañas LISTO
#Validaciones username unico LISTO  
#Combobox muestre los vehiculos ID e usuarios ID etc. LISTO
#Solo si tiene las piezas necesarias para la reparación lo puede hacer LISTO
#Validar por usuario los clientes que tenga LISTO
#Cuando ingresa con el perfil de admin puede ver todos los clientes que tiene registrado LISTO
#Validaciones de fechas en entradas y salidas de datos LISTO
#Que sea congruente la información osea entre el 5 de octubre pero no pueda salir antes de esa fecha LISTO

#Secretaria tambien tiene los vehiculos LISTO
#Secretaria clientes y vehiculos LISTO
#Secretario o gerente clientes que aparezcan LISTO 

#Validaciones de cada perfil LISTO


def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="taller_mecanico"
    )


def verificar_usuario(username, password):
    conn = conectar_db()
    cursor = conn.cursor()

    query = "SELECT id, password, role FROM usuarios WHERE username = %s"
    cursor.execute(query, (username,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and password == result[1]:  
        return result[0], result[2]  
    return None, None  



def login():
    global user_logged_in_id, rol_actual, nuevo_usuario, nueva_password, nuevo_rol, nombre_usuario, apellido_paterno, apellido_materno, telefono, direccion
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Por favor llena todos los campos.")
        return

    user_id, perfil = verificar_usuario(username, password) #Se obtiene el ID y el ROL

    if user_id is None or perfil is None:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        return

    user_logged_in_id = user_id 

    rol_actual = perfil  # Almacenar el rol del usuario logeado

    for tab in [tab_usuarios, tab_clientes, tab_vehiculos, tab_reparaciones, tab_piezas]:
        for widget in tab.winfo_children():
            widget.destroy()



    # Acceso total para "Root", "Admin" y "Gerente"
    if rol_actual in ["Root", "Admin", "Gerente"]:
        notebook.add(tab_usuarios, text="Usuarios")
        notebook.add(tab_clientes, text="Clientes")
        notebook.add(tab_vehiculos, text="Vehiculos")
        notebook.add(tab_reparaciones, text="Reparaciones")
        notebook.add(tab_piezas, text="Piezas")    
        notebook.add(tab_vista_general, text="Vista General")


    elif rol_actual == "Secretaria":
        notebook.add(tab_clientes, text="Clientes")
        notebook.add(tab_vehiculos, text="Vehiculos")
        notebook.add(tab_vista_general_secretaria, text="Vista General Secretaria")    


    elif rol_actual == "Mecanico":
        notebook.add(tab_reparaciones, text="Reparaciones")
        notebook.add(tab_piezas, text="Piezas")
        notebook.add(tab_vista_general_mecanico, text="Vista General Mecanico")    



    messagebox.showinfo("Bienvenido", f"Bienvenido {username} con perfil {perfil} e ID = {user_logged_in_id}.")

    usuarios_tab_layout()
    clientes_tab_layout()
    actualizar_combobox_usuarios()
    vehiculos_tab_layout()
    actualizar_combobox_clientes()
    actualizar_combobox_mecanicos()
    reparaciones_tab_layout()
    actualizar_combobox_vehiculos()
    piezas_tab_layout()
    actualizar_combobox_piezas()
    vista_general_tab_layout()
    vista_general_mecanico_tab_layout()
    vista_general_secretaria_tab_layout()


    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

    if nuevo_usuario and nueva_password:
        nuevo_usuario.delete(0, tk.END)
        nueva_password.delete(0, tk.END)
        nuevo_rol.set("")


def logout():
    global user_logged_in_id, rol_actual, nombre_usuario, apellido_paterno, apellido_materno, telefono, direccion
    if rol_actual is None:
        messagebox.showwarning("Advertencia", "Ningún usuario ha iniciado sesión.")
        return

    tabs_to_forget = [tab_usuarios, tab_clientes, tab_vehiculos, tab_reparaciones, tab_piezas, tab_vista_general, tab_vista_general_secretaria, tab_vista_general_mecanico]
    
    for tab in tabs_to_forget:
        try:
            notebook.index(tab)  
            notebook.forget(tab) 
        except tk.TclError:  
            pass  

    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    
    if nombre_usuario:
        nombre_usuario.delete(0, tk.END)
    if apellido_paterno:
        apellido_paterno.delete(0, tk.END)
    if apellido_materno:
        apellido_materno.delete(0, tk.END)
    if telefono:
        telefono.delete(0, tk.END)
    if direccion:
        direccion.delete(0, tk.END)

    rol_actual = None
    user_logged_in_id = None


######################################################-------FUNCIONES PESTAÑAS -----------########################################################################

def add_labels_and_entries(tab, labels, start_row=0, search_entry=None):
    for idx, label in enumerate(labels, start=start_row):
        tk.Label(tab, text=label).grid(row=idx, column=0, pady=10, padx=10, sticky="e")
        entry = tk.Entry(tab)
        entry.grid(row=idx, column=1, pady=10, padx=10, columnspan=2, sticky="we")
        
        if entry != search_entry:
            entry['state'] = 'disabled'


######################################################-------PESTAÑA REPARACIONES-----------########################################################################

def add_action_buttons_reparaciones(tab, row):
    BUTTON_WIDTH = 15
    actions = ["Nuevo", "Salvar", "Cancelar", "Editar", "Remover"]

    for idx, action in enumerate(actions):
        if action == "Nuevo":
            btn_command = nuevo_reparacion
            button_state = "normal" 
        elif action == "Salvar":
            btn_command = salvar_reparacion
            button_state = "disabled"  
        elif action == "Buscar":
            btn_command = None  
            button_state = "normal"  
        elif action == "Editar":
            btn_command = editar_reparacion 
        elif action == "Cancelar":
            btn_command = cancelar_reparacion
            button_state = "disabled"
        elif action == "Remover":
            btn_command = remover_reparacion
            button_state = "disabled"
            
        else:
            btn_command = None  
            button_state = "disabled" 

        tk.Button(tab, text=action, width=BUTTON_WIDTH, state=button_state, command=btn_command).grid(row=row, column=idx, pady=10, padx=10, sticky="w")


######################################################-------PESTAÑA PIEZAS-----------########################################################################


def add_action_buttons_piezas(tab, row):
    BUTTON_WIDTH = 15
    actions = ["Nuevo", "Salvar", "Cancelar", "Editar", "Remover"]

    for idx, action in enumerate(actions):
        if action == "Nuevo":
            btn_command = nuevo_pieza
            button_state = "normal"  
        elif action == "Salvar":
            btn_command = salvar_pieza
            button_state = "disabled"  
        elif action == "Buscar":
            btn_command = None  
            button_state = "normal"  
        elif action == "Editar":
            btn_command = editar_pieza  
        elif action == "Cancelar":
            btn_command = cancelar_pieza
            button_state = "disabled"
        elif action == "Remover":
            btn_command = remover_pieza
            button_state = "disabled"
            
        else:
            btn_command = None  
            button_state = "disabled" 

        tk.Button(tab, text=action, width=BUTTON_WIDTH, state=button_state, command=btn_command).grid(row=row, column=idx, pady=10, padx=10, sticky="w")


######################################################-------PESTAÑA VEHICULOS-----------########################################################################


def add_action_buttons_vehiculos(tab, row):
    BUTTON_WIDTH = 15
    actions = ["Nuevo", "Salvar", "Cancelar", "Editar", "Remover"]

    for idx, action in enumerate(actions):
        if action == "Nuevo":
            btn_command = nuevo_vehiculo
            button_state = "normal"
        elif action == "Salvar":
            btn_command = salvar_vehiculo
            button_state = "disabled" 
        elif action == "Buscar":
            btn_command = None  
            button_state = "normal"  
        elif action == "Editar":
            btn_command = editar_vehiculo  
        elif action == "Cancelar":
            btn_command = cancelar_vehiculo
            button_state = "disabled"
        elif action == "Remover":
            btn_command = remover_vehiculo
            button_state = "disabled"
            
        else:
            btn_command = None  
            button_state = "disabled"  

        tk.Button(tab, text=action, width=BUTTON_WIDTH, state=button_state, command=btn_command).grid(row=row, column=idx, pady=10, padx=10, sticky="w")




######################################################-------PESTAÑA CLIENTES-----------########################################################################

def add_action_buttons_clientes(tab, row):
    BUTTON_WIDTH = 15
    actions = ["Nuevo", "Salvar", "Cancelar", "Editar", "Remover"]

    for idx, action in enumerate(actions):
        if action == "Nuevo":
            btn_command = nuevo_cliente1
            button_state = "normal"  
        elif action == "Salvar":
            btn_command = salvar_cliente
            button_state = "disabled" 
        elif action == "Cancelar":
            btn_command = cancelar_cliente  
            button_state = "normal" 
        elif action == "Buscar":
            btn_command = None  
            button_state = "normal" 
        elif action == "Editar":
            btn_command = editar_cliente
            button_state = "disabled"
        elif action == "Remover":
            btn_command = remover_cliente
            button_state = "disabled"
        else:
            btn_command = None  
            button_state = "disabled" 

        tk.Button(tab, text=action, width=BUTTON_WIDTH, state=button_state, command=btn_command).grid(row=row, column=idx, pady=10, padx=10, sticky="w")


######################################################-------PESTAÑA USUARIOS-----------########################################################################


def add_action_buttons_usuarios(tab, row):
    BUTTON_WIDTH = 15
    actions = ["Nuevo", "Salvar", "Cancelar", "Editar", "Remover"]

    for idx, action in enumerate(actions):
        if action == "Nuevo":
            btn_command = nuevo_usuario
            button_state = "normal" 
        elif action == "Salvar":
            btn_command = salvar_usuario
            button_state = "disabled"  
        elif action == "Buscar":
            btn_command = None  
            button_state = "normal"  
        elif action == "Editar":
            btn_command = editar_usuario
        elif action == "Cancelar":
            btn_command = cancelar
            button_state = "disabled"
        elif action == "Remover":
            btn_command = remover_usuario
            button_state = "disabled"
            
        else:
            btn_command = None  
            button_state = "disabled" 

        tk.Button(tab, text=action, width=BUTTON_WIDTH, state=button_state, command=btn_command).grid(row=row, column=idx, pady=10, padx=10, sticky="w")

def configure_columns(tab, columns):
    for idx, weight in enumerate(columns):
        tab.grid_columnconfigure(idx, weight=weight)

def add_padding(tab):
    for child in tab.winfo_children():
        child.grid_configure(padx=5, pady=5)


######################################################-------FUNCIONES BOTONES USUARIOS-----------########################################################################

def buscar_usuario():
    global modo_formulario  

    
    conn = conectar_db()
    cursor = conn.cursor()

    search_entry = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    user_id_str = search_entry.get()
    if not user_id_str:
        messagebox.showerror("Error", "Por favor ingrese un ID válido.")
        return
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        messagebox.showerror("Error", "El ID debe ser un número entero.")
        return

    query = "SELECT * FROM usuarios WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:  
        messagebox.showerror("Error", "No se encontró un usuario con ese ID.")
        return

    modo_formulario = "editar"  

    entries_order = [0, 4, 5, 6, 7, 1, 8, 2, 3]
    entries = [widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry) and widget != search_entry]
    
    for idx, value in enumerate(entries_order):
        entries[idx]['state'] = 'normal'
        entries[idx].delete(0, tk.END)
        entries[idx].insert(0, result[value])
        entries[idx]['state'] = 'readonly'
        
    perfil_combo = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, ttk.Combobox))
    perfil_combo['state'] = 'normal'
    perfil_combo.set(result[3])
    perfil_combo['state'] = 'readonly'

    for widget in tab_usuarios.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'normal'
            elif widget['text'] == "Salvar":
                widget['state'] = 'disabled'

def cancelar():
    global modo_formulario  
    
    modo_formulario = "none"  

    entries = [widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry.delete(0, tk.END)
        entry['state'] = 'disabled'

    id_buscar_entry = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    id_buscar_entry['state'] = 'normal'

    for widget in tab_usuarios.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Nuevo", "Buscar"]:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'


def remover_usuario():
    search_entry = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    user_id_str = search_entry.get()

    answer = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar a este usuario?")
    
    if not answer:  
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(query, (user_id_str,))
        conn.commit()
        
        messagebox.showinfo("Información", "Usuario eliminado exitosamente.")
        search_entry.delete(0, tk.END)
        for widget in tab_usuarios.winfo_children():
            if isinstance(widget, tk.Entry) and widget != search_entry:
                widget['state'] = 'normal'
                widget.delete(0, tk.END)
                widget['state'] = 'readonly'
            elif isinstance(widget, ttk.Combobox):
                widget['state'] = 'normal'
                widget.set('')
                widget['state'] = 'readonly'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'disabled'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al eliminar el usuario: {e}")

    cursor.close()
    conn.close()


def nuevo_usuario():
    global modo_formulario  
    
    modo_formulario = "nuevo"  

    entries = [widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry['state'] = 'normal'
        entry.delete(0, tk.END)

    id_entry = entries[1]  
    next_id = obtener_proximo_id()
    id_entry.insert(0, str(next_id))
    id_entry['state'] = 'readonly'  

    id_buscar_entry = entries[0]  
    id_buscar_entry['state'] = 'readonly'

    for widget in tab_usuarios.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'
        elif isinstance(widget, tk.Button) and widget['text'] == "Cancelar":
            widget['state'] = 'normal'



def obtener_proximo_id():
    conn = conectar_db()
    cursor = conn.cursor()

    query = "SELECT MAX(id) FROM usuarios"
    cursor.execute(query)
    max_id = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    if max_id is None:
        return 1
    else:
        return max_id + 1


def editar_usuario():
    global modo_formulario 
    
    modo_formulario = "editar"  
    
    entries = [widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        if entry.grid_info()['row'] not in [0, 1]:  
            entry['state'] = 'normal'

    perfil_combo = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, ttk.Combobox))
    perfil_combo['state'] = 'normal'

    for widget in tab_usuarios.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'


def salvar_usuario():
    global modo_formulario

    conn = conectar_db()
    cursor = conn.cursor()

    entries_order = [6, 8, 2, 3, 4, 5, 7]
    values = []

    entries = [widget for widget in tab_usuarios.winfo_children() if isinstance(widget, tk.Entry)]
    username = entries[6].get()
    
    # Verificar si el nombre de usuario ya existe
    if modo_formulario == "nuevo" and username_existe(username):
        messagebox.showerror("Error", "Ya existe un usuario con ese nombre de usuario. Por favor, elige otro.")
        return
    elif modo_formulario == "editar":
        user_id = entries[0].get()
        if username_existe(username, user_id):
            messagebox.showerror("Error", "Ya existe otro usuario con ese nombre de usuario. Por favor, elige otro.")
            return

    for idx in entries_order[:-1]:
        values.append(entries[idx].get())

    perfil_combo = next(widget for widget in tab_usuarios.winfo_children() if isinstance(widget, ttk.Combobox))
    role = perfil_combo.get()
    values.insert(2, role)

    values.append(entries[entries_order[-1]].get())

    if modo_formulario == "nuevo":
        query = "INSERT INTO usuarios (username, password, role, nombre, apellido_paterno, apellido_materno, telefono, direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    elif modo_formulario == "editar":
        values.append(user_id)
        query = "UPDATE usuarios SET username=%s, password=%s, role=%s, nombre=%s, apellido_paterno=%s, apellido_materno=%s, telefono=%s, direccion=%s WHERE id=%s"
    else:
        messagebox.showerror("Error", "Modo desconocido.")
        return

    try:
        print(values)
        cursor.execute(query, tuple(values))
        conn.commit()

        if modo_formulario == "nuevo":
            messagebox.showinfo("Información", "Usuario guardado exitosamente.")
        elif modo_formulario == "editar":
            messagebox.showinfo("Información", "Usuario actualizado exitosamente.")

        for entry in entries:
            entry['state'] = 'readonly'
        perfil_combo['state'] = 'readonly'

        for widget in tab_usuarios.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] in ["Salvar"]:
                widget['state'] = 'disabled'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Nuevo", "Cancelar"]:
                widget['state'] = 'normal'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar el usuario: {e}")

    actualizar_combobox_usuarios()
    cursor.close()
    conn.close()



def username_existe(username, user_id=None):
    conn = conectar_db()
    cursor = conn.cursor()

    if user_id:
        query = "SELECT * FROM usuarios WHERE username = %s AND id != %s"
        cursor.execute(query, (username, user_id))
    else:
        query = "SELECT * FROM usuarios WHERE username = %s"
        cursor.execute(query, (username,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return True if result else False


######################################################-------PESTAÑA REPARACIONES-----------########################################################################
def obtener_stock_pieza(pieza_id):
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT stock FROM piezas WHERE pieza_id = %s"
    cursor.execute(query, (pieza_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return 0


def actualizar_stock_pieza(pieza_id, nueva_cantidad):
    conn = conectar_db()
    cursor = conn.cursor()
    query = "UPDATE piezas SET stock = %s WHERE pieza_id = %s"
    cursor.execute(query, (nueva_cantidad, pieza_id))
    conn.commit()
    cursor.close()
    conn.close()


def obtener_piezas():
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT pieza_id FROM piezas"
    cursor.execute(query)  
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [item[0] for item in result]

def actualizar_combobox_piezas():
    global id_pieza_combobox
    piezas = obtener_piezas()
    print(piezas)
    id_pieza_combobox['values'] = piezas


def obtener_vehiculos_por_cliente_usuario(user_id):
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT vehiculo_id FROM vehiculos WHERE id_mecanico = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [item[0] for item in result]

def actualizar_combobox_vehiculos():
    global id_vehiculo_combobox
    vehiculos = obtener_vehiculos_por_cliente_usuario(user_logged_in_id)
    print(vehiculos)
    id_vehiculo_combobox['values'] = vehiculos


def buscar_reparacion():
    global modo_formulario_reparaciones 
    
    conn = conectar_db()
    cursor = conn.cursor()

    search_entry = next(widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    reparaciones_id_str = search_entry.get()

    if not reparaciones_id_str:
        messagebox.showerror("Error", "Por favor ingrese un ID válido.")
        return

    try:
        reparaciones_id = int(reparaciones_id_str)
    except ValueError:
        messagebox.showerror("Error", "El ID debe ser un número entero.")
        return

    query = "SELECT * FROM reparaciones WHERE reparacion_id = %s"
    cursor.execute(query, (reparaciones_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        messagebox.showerror("Error", "No se encontró un vehiculo con ese ID.")
        return
    
    modo_formulario_reparaciones = "editar"  

    entries_order = [0, 0, 0, 3, 4, 5, 6]  
    entries = [widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry) and widget != search_entry]
    
    for idx, value in enumerate(entries_order):
        entries[idx]['state'] = 'normal'
        entries[idx].delete(0, tk.END)
        entries[idx].insert(0, result[value])
        entries[idx]['state'] = 'readonly'
        
    id_vehiculo_combobox = tab_reparaciones.nametowidget("vehiculo_combobox")
    id_vehiculo_combobox['state'] = 'normal'
    id_vehiculo_combobox.set(result[1])
    id_vehiculo_combobox['state'] = 'readonly'

    id_pieza_combobox = tab_reparaciones.nametowidget("pieza_combobox")
    id_pieza_combobox['state'] = 'normal'
    id_pieza_combobox.set(result[2])
    id_pieza_combobox['state'] = 'readonly'

    for widget in tab_reparaciones.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'normal'
            elif widget['text'] == "Salvar":
                widget['state'] = 'disabled'


def nuevo_reparacion():
    global modo_formulario_reparaciones  
    
    modo_formulario_reparaciones = "nuevo"  

    entries = [widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry['state'] = 'normal'
        entry.delete(0, tk.END)

    id_entry = entries[3]  
    next_id = get_next_reparaciones_id()
    id_entry.insert(0, str(next_id))
    id_entry['state'] = 'readonly'  

    id_buscar_entry = entries[0]  
    id_buscar_entry['state'] = 'readonly'
    
    for widget in tab_reparaciones.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'
        elif isinstance(widget, tk.Button) and widget['text'] == "Cancelar":
            widget['state'] = 'normal'



def get_next_reparaciones_id():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(reparacion_id) FROM reparaciones")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result[0] is None:
        return 1
    return result[0] + 1

def validar_formato_fecha(fecha):
    try:
        datetime.datetime.strptime(fecha, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def validar_fechas_entrada_salida(fecha_entrada, fecha_salida):
    fecha_entrada_obj = datetime.datetime.strptime(fecha_entrada, "%d-%m-%Y")
    fecha_salida_obj = datetime.datetime.strptime(fecha_salida, "%d-%m-%Y")
    return fecha_salida_obj >= fecha_entrada_obj


def salvar_reparacion():
    global modo_formulario_reparaciones

    conn = conectar_db()
    cursor = conn.cursor()

    entries = [widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry)]
    
    vehiculo_id = entries[1].get()  
    pieza_id = entries[2].get()
    reparacion_id = entries[3].get()
    fecha_entrada = entries[4].get()
    fecha_salida = entries[5].get()
    falla = entries[6].get()
    cantidad_piezas = entries[7].get()

    values = [vehiculo_id, pieza_id, fecha_entrada, fecha_salida, falla, cantidad_piezas, reparacion_id]  
    cantidad_piezas_solicitadas = int(cantidad_piezas)
    stock_actual = obtener_stock_pieza(pieza_id)

    if cantidad_piezas_solicitadas > stock_actual:
        messagebox.showerror("Error", f"No hay suficiente stock para la pieza seleccionada. Stock actual: {stock_actual}")
        return
    
    if not validar_formato_fecha(fecha_entrada) or not validar_formato_fecha(fecha_salida):
        messagebox.showerror("Error", "El formato de la fecha es incorrecto. Debe ser dd-mm-aaaa.")
        return

    if not validar_fechas_entrada_salida(fecha_entrada, fecha_salida):
        messagebox.showerror("Error", "La fecha de salida no puede ser anterior a la fecha de entrada.")
        return

    nuevo_stock = stock_actual - cantidad_piezas_solicitadas
    actualizar_stock_pieza(pieza_id, nuevo_stock)

    if modo_formulario_reparaciones == "nuevo":
        query = "INSERT INTO reparaciones (vehiculo_id, pieza_id, fecha_entrada, fecha_salida, falla, cantidad_piezas) VALUES (%s, %s, %s, %s, %s, %s)"
        
        values.pop()
    elif modo_formulario_reparaciones == "editar":
        query = "UPDATE reparaciones SET vehiculo_id=%s, pieza_id=%s, fecha_entrada=%s, fecha_salida=%s, falla=%s, cantidad_piezas=%s  WHERE reparacion_id=%s"
    else:
        messagebox.showerror("Error", "Modo desconocido.")
        return

    try:
        cursor.execute(query, tuple(values))
        conn.commit()

        if modo_formulario_reparaciones == "nuevo":
            messagebox.showinfo("Información", "Reparación guardada exitosamente.")
        elif modo_formulario_reparaciones == "editar":
            messagebox.showinfo("Información", "Reparación actualizada exitosamente.")
        
        for entry in entries:
            entry['state'] = 'readonly'

        for widget in tab_reparaciones.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] in ["Salvar"]:
                widget['state'] = 'disabled'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Nuevo", "Cancelar"]:
                widget['state'] = 'normal'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar la reparación: {e}")

    cursor.close()
    conn.close()


def editar_reparacion():
    global modo_formulario_reparaciones  
    
    modo_formulario_reparaciones = "editar" 
    
    entries = [widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        if entry.grid_info()['row'] not in [0, 3]:  
            entry['state'] = 'normal'

    id_vehiculo_combobox = next(widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, ttk.Combobox))
    id_vehiculo_combobox['state'] = 'normal'

    id_pieza_combobox = next(widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, ttk.Combobox))
    id_pieza_combobox['state'] = 'normal'

    for widget in tab_reparaciones.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'

def remover_reparacion():
    search_entry = next(widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    reparaciones_id_str = search_entry.get()

    answer = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta reparación?")
    
    if not answer:  
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM reparaciones WHERE reparacion_id = %s"
        cursor.execute(query, (reparaciones_id_str,))
        conn.commit()
        
        messagebox.showinfo("Información", "Reparación eliminada exitosamente.")
        search_entry.delete(0, tk.END)
        for widget in tab_reparaciones.winfo_children():
            if isinstance(widget, tk.Entry) and widget != search_entry:
                widget['state'] = 'normal'
                widget.delete(0, tk.END)
                widget['state'] = 'readonly'
            elif isinstance(widget, ttk.Combobox):
                widget['state'] = 'normal'
                widget.set('')
                widget['state'] = 'readonly'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'disabled'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al eliminar la reparación: {e}")

    cursor.close()
    conn.close()

def cancelar_reparacion():
    global modo_formulario_reparaciones
    
    modo_formulario_reparaciones = "none"  

    entries = [widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry.delete(0, tk.END)
        entry['state'] = 'disabled'

    id_buscar_entry = next(widget for widget in tab_reparaciones.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    id_buscar_entry['state'] = 'normal'

    for widget in tab_reparaciones.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Nuevo", "Buscar"]:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'

    for widget in tab_reparaciones.winfo_children():
        if isinstance(widget, ttk.Combobox):
            widget.set('')  
            widget['state'] = 'disabled'  


######################################################-------PESTAÑA VEHICULOS-----------########################################################################

def obtener_clientes_por_usuario(user_id):
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT cliente_id FROM clientes WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [item[0] for item in result]


def actualizar_combobox_clientes():
    global id_cliente_combobox
    clientes = obtener_clientes_por_usuario(user_logged_in_id)
    print(clientes)
    id_cliente_combobox['values'] = clientes

def obtener_mecanicos():
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT id FROM usuarios WHERE role = 'Mecanico'"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [item[0] for item in result]


def actualizar_combobox_mecanicos():
    global id_cliente_combobox
    mecanicos = obtener_mecanicos()
    print(mecanicos)
    id_mecanico_combobox['values'] = mecanicos





def buscar_vehiculo():
    global modo_formulario_vehiculos
    
    conn = conectar_db()
    cursor = conn.cursor()

    search_entry = next(widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    vehiculos_id_str = search_entry.get()

    if not vehiculos_id_str:
        messagebox.showerror("Error", "Por favor ingrese un ID válido.")
        return

    try:
        vehiculos_id = int(vehiculos_id_str)
    except ValueError:
        messagebox.showerror("Error", "El ID debe ser un número entero.")
        return

    query = "SELECT * FROM vehiculos WHERE vehiculo_id = %s"
    cursor.execute(query, (vehiculos_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        messagebox.showerror("Error", "No se encontró un vehiculo con ese ID.")
        return
    
    modo_formulario_vehiculos = "editar"  

    entries_order = [0, 0, 0, 2, 3, 4, 5]  
    entries = [widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry) and widget != search_entry]
    
    for idx, value in enumerate(entries_order):
        entries[idx]['state'] = 'normal'
        entries[idx].delete(0, tk.END)
        entries[idx].insert(0, result[value])
        entries[idx]['state'] = 'readonly'
        
    id_cliente_combobox = tab_vehiculos.nametowidget("cliente_combobox_1")
    id_cliente_combobox['state'] = 'normal'
    id_cliente_combobox.set(result[1])
    id_cliente_combobox['state'] = 'readonly'

    id_mecanico_combobox = tab_vehiculos.nametowidget("mecanico_combobox")
    id_mecanico_combobox['state'] = 'normal'
    id_mecanico_combobox.set(result[6])
    id_mecanico_combobox['state'] = 'readonly'

    for widget in tab_vehiculos.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'normal'
            elif widget['text'] == "Salvar":
                widget['state'] = 'disabled'



def nuevo_vehiculo():
    global modo_formulario_vehiculos  
    
    modo_formulario_vehiculos = "nuevo"  

    entries = [widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry['state'] = 'normal'
        entry.delete(0, tk.END)

    id_entry = entries[3]  
    next_id = get_next_vehiculos_id()
    id_entry.insert(0, str(next_id))
    id_entry['state'] = 'readonly'  

    id_buscar_entry = entries[0]  
    id_buscar_entry['state'] = 'readonly'

    for widget in tab_vehiculos.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'
        elif isinstance(widget, tk.Button) and widget['text'] == "Cancelar":
            widget['state'] = 'normal'



def get_next_vehiculos_id():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(vehiculo_id) FROM vehiculos")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result[0] is None:
        return 1
    return result[0] + 1

def salvar_vehiculo():
    global modo_formulario_vehiculos 

    conn = conectar_db()
    cursor = conn.cursor()

    cliente_id_seleccionado = id_cliente_combobox.get()
    mecanico_id_seleccionado = id_mecanico_combobox.get()

    entries = [widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry)]
    
    vehiculo_id = entries[3].get()  
    matricula = entries[4].get()
    marca = entries[5].get()
    modelo = entries[6].get()
    fecha = entries[7].get()

    values = [cliente_id_seleccionado, mecanico_id_seleccionado, matricula, marca, modelo, fecha, vehiculo_id]  

    cursor.execute("SELECT vehiculo_id FROM vehiculos WHERE matricula = %s", (matricula,))
    existing_vehiculo = cursor.fetchone()
    if existing_vehiculo:
        if modo_formulario_vehiculos == "nuevo" or (modo_formulario_vehiculos == "editar" and str(existing_vehiculo[0]) != vehiculo_id):
            messagebox.showerror("Error", "Ya existe un vehículo con esa matrícula. Cada matrícula debe ser única.")
            return

    if not re.match(r"^[A-Za-z]{3}-\d{3}$", matricula):
        messagebox.showerror("Error", "La matrícula ingresada no tiene el formato correcto. Debe ser tres letras seguidas por un guion y luego tres números. Ejemplo: ABC-123.")
        return

    if modo_formulario_vehiculos == "nuevo":
        query = "INSERT INTO vehiculos (cliente_id, id_mecanico, matricula, marca, modelo, fecha) VALUES (%s, %s, %s, %s, %s, %s)"
        
        values.pop()
    elif modo_formulario_vehiculos == "editar":
        query = "UPDATE vehiculos SET cliente_id=%s, id_mecanico=%s, matricula=%s, marca=%s, modelo=%s, fecha=%s WHERE vehiculo_id=%s"
    else:
        messagebox.showerror("Error", "Modo desconocido.")
        return

    try:
        cursor.execute(query, tuple(values))
        conn.commit()

        if modo_formulario_vehiculos == "nuevo":
            messagebox.showinfo("Información", "Vehiculo guardado exitosamente.")
        elif modo_formulario_vehiculos == "editar":
            messagebox.showinfo("Información", "Vehiculo actualizado exitosamente.")
        
        for entry in entries:
            entry['state'] = 'readonly'

        for widget in tab_vehiculos.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
                widget['state'] = 'disabled'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Nuevo", "Cancelar"]:
                widget['state'] = 'normal'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar el vehiculo: {e}")
    actualizar_combobox_vehiculos()
    cursor.close()
    conn.close()


def editar_vehiculo():
    global modo_formulario_vehiculos 
    
    modo_formulario_vehiculos = "editar"  
    
    entries = [widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        if entry.grid_info()['row'] not in [0, 3]:  
            entry['state'] = 'normal'

    id_cliente_combobox = next(widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, ttk.Combobox))
    id_cliente_combobox['state'] = 'normal'

    for widget in tab_vehiculos.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'

def remover_vehiculo():
    search_entry = next(widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    vehiculos_id_str = search_entry.get()

    answer = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar a este vehiculo?")
    
    if not answer:  
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM vehiculos WHERE vehiculo_id = %s"
        cursor.execute(query, (vehiculos_id_str,))
        conn.commit()
        
        messagebox.showinfo("Información", "Vehiculo eliminado exitosamente.")
        search_entry.delete(0, tk.END)
        for widget in tab_vehiculos.winfo_children():
            if isinstance(widget, tk.Entry) and widget != search_entry:
                widget['state'] = 'normal'
                widget.delete(0, tk.END)
                widget['state'] = 'readonly'
            elif isinstance(widget, ttk.Combobox):
                widget['state'] = 'normal'
                widget.set('')
                widget['state'] = 'readonly'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'disabled'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al eliminar el vehiculo: {e}")

    cursor.close()
    conn.close()

def cancelar_vehiculo():
    global modo_formulario_vehiculos 
    
    modo_formulario_vehiculos = "none"  

    entries = [widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry.delete(0, tk.END)
        entry['state'] = 'disabled'

    id_buscar_entry = next(widget for widget in tab_vehiculos.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    id_buscar_entry['state'] = 'normal'

    for widget in tab_vehiculos.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Nuevo", "Buscar"]:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'

    for widget in tab_vehiculos.winfo_children():
        if isinstance(widget, ttk.Combobox):
            widget.set('')  
            widget['state'] = 'disabled'  



def matricula_existe(matricula, vehiculo_id=None):
    conn = conectar_db()
    cursor = conn.cursor()

    if vehiculo_id:
        query = "SELECT * FROM vehiculos WHERE matricula = %s AND vehiculo_id != %s"
        cursor.execute(query, (matricula, vehiculo_id))
    else:
        query = "SELECT * FROM vehiculos WHERE matricula = %s"
        cursor.execute(query, (matricula,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return True if result else False


######################################################-------PESTAÑA PIEZAS-----------########################################################################

def buscar_pieza():
    global modo_formulario_piezas  
    
    conn = conectar_db()
    cursor = conn.cursor()

    search_entry = next(widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    pieza_id_str = search_entry.get()

    if not pieza_id_str:
        messagebox.showerror("Error", "Por favor ingrese un ID válido.")
        return
    try:
        pieza_id = int(pieza_id_str)
    except ValueError:
        messagebox.showerror("Error", "El ID debe ser un número entero.")
        return

    query = "SELECT * FROM piezas WHERE pieza_id = %s"
    cursor.execute(query, (pieza_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        messagebox.showerror("Error", "No se encontró una pieza con ese ID.")
        return
    
    modo_formulario_piezas = "editar"  

    entries_order = [0,2,1]  
    entries = [widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry) and widget != search_entry]
    
    for idx, value in enumerate(entries_order):
        entries[idx]['state'] = 'normal'
        entries[idx].delete(0, tk.END)
        entries[idx].insert(0, result[value])
        entries[idx]['state'] = 'readonly'

    for widget in tab_piezas.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'normal'
            elif widget['text'] == "Salvar":
                widget['state'] = 'disabled'


def nuevo_pieza():
    global modo_formulario_piezas 
    
    modo_formulario_piezas = "nuevo"  

    entries = [widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry['state'] = 'normal'
        entry.delete(0, tk.END)

    id_entry = entries[1]  
    next_id = get_next_pieza_id()
    id_entry.insert(0, str(next_id))
    id_entry['state'] = 'readonly'  


    id_buscar_entry = entries[0]  
    id_buscar_entry['state'] = 'readonly'

    for widget in tab_piezas.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'
        elif isinstance(widget, tk.Button) and widget['text'] == "Cancelar":
            widget['state'] = 'normal'



def get_next_pieza_id():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(pieza_id) FROM piezas")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result[0] is None:
        return 1
    return result[0] + 1

def salvar_pieza():
    global modo_formulario_piezas  

    conn = conectar_db()
    cursor = conn.cursor()

    entries = [widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry)]
    
    pieza_id = entries[1].get()  
    descripcion = entries[2].get()
    stock = entries[3].get()

    values = [descripcion, stock, pieza_id]  

    if modo_formulario_piezas == "nuevo":
        query = "INSERT INTO piezas (descripcion, stock) VALUES (%s, %s)"
        values.pop()
    elif modo_formulario_piezas == "editar":
        query = "UPDATE piezas SET descripcion=%s, stock=%s WHERE pieza_id=%s"
    else:
        messagebox.showerror("Error", "Modo desconocido.")
        return

    try:
        cursor.execute(query, tuple(values))
        conn.commit()

        if modo_formulario_piezas == "nuevo":
            messagebox.showinfo("Información", "Pieza guardada exitosamente.")
        elif modo_formulario_piezas == "editar":
            messagebox.showinfo("Información", "Pieza actualizada exitosamente.")
        
        for entry in entries:
            entry['state'] = 'readonly'

        for widget in tab_piezas.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
                widget['state'] = 'disabled'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Nuevo", "Cancelar"]:
                widget['state'] = 'normal'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar la pieza: {e}")
    actualizar_combobox_piezas()
    cursor.close()
    conn.close()


def editar_pieza():
    global modo_formulario_piezas  
    
    modo_formulario_piezas = "editar" 
    
    entries = [widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        if entry.grid_info()['row'] not in [0, 2]:  
            entry['state'] = 'normal'

    for widget in tab_piezas.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'

def remover_pieza():
    search_entry = next(widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    pieza_id_str = search_entry.get()

    answer = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta pieza?")
    
    if not answer:  
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM piezas WHERE pieza_id = %s"
        cursor.execute(query, (pieza_id_str,))
        conn.commit()
        
        messagebox.showinfo("Información", "Pieza eliminado exitosamente.")
        search_entry.delete(0, tk.END)
        for widget in tab_piezas.winfo_children():
            if isinstance(widget, tk.Entry) and widget != search_entry:
                widget['state'] = 'normal'
                widget.delete(0, tk.END)
                widget['state'] = 'readonly'
            elif isinstance(widget, ttk.Combobox):
                widget['state'] = 'normal'
                widget.set('')
                widget['state'] = 'readonly'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'disabled'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al eliminar el cliente: {e}")

    cursor.close()
    conn.close()

def cancelar_pieza():
    global modo_formulario_piezas  
    
    modo_formulario_piezas = "none"  

    entries = [widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry.delete(0, tk.END)
        entry['state'] = 'disabled'

    id_buscar_entry = next(widget for widget in tab_piezas.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    id_buscar_entry['state'] = 'normal'

    for widget in tab_piezas.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Nuevo", "Buscar"]:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'






######################################################-------PESTAÑA CLIENTES-----------########################################################################

def obtener_usuarios():
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT id FROM usuarios order by id asc"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [item[0] for item in result]

def actualizar_combobox_usuarios():
    global id_usuario_combobox
    usuarios = obtener_usuarios()
    print(usuarios)
    id_usuario_combobox['values'] = usuarios





def buscar_cliente():
    global modo_formulario_clientes  
    
    conn = conectar_db()
    cursor = conn.cursor()

    search_entry = next(widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    cliente_id_str = search_entry.get()

    if not cliente_id_str:
        messagebox.showerror("Error", "Por favor ingrese un ID válido.")
        return

    try:
        cliente_id = int(cliente_id_str)
    except ValueError:
        messagebox.showerror("Error", "El ID debe ser un número entero.")
        return

    query = "SELECT * FROM clientes WHERE cliente_id = %s"
    cursor.execute(query, (cliente_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        messagebox.showerror("Error", "No se encontró un cliente con ese ID.")
        return
    
    modo_formulario_clientes = "editar"  

    entries_order = [0,0,2, 3, 4]  
    entries = [widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry) and widget != search_entry]
    
    for idx, value in enumerate(entries_order):
        entries[idx]['state'] = 'normal'
        entries[idx].delete(0, tk.END)
        entries[idx].insert(0, result[value])
        entries[idx]['state'] = 'readonly'
        
    id_usuario_combobox = next(widget for widget in tab_clientes.winfo_children() if isinstance(widget, ttk.Combobox))
    id_usuario_combobox['state'] = 'normal'
    id_usuario_combobox.set(result[1])  
    id_usuario_combobox['state'] = 'readonly'

    for widget in tab_clientes.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'normal'
            elif widget['text'] == "Salvar":
                widget['state'] = 'disabled'


def nuevo_cliente1():
    global modo_formulario_clientes  
    
    modo_formulario_clientes = "nuevo"  

    entries = [widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry['state'] = 'normal'
        entry.delete(0, tk.END)

    id_entry = entries[2]  
    next_id = get_next_cliente_id()
    id_entry.insert(0, str(next_id))
    id_entry['state'] = 'readonly'  

    id_buscar_entry = entries[0] 
    id_buscar_entry['state'] = 'readonly'
    
    # Setear el ID del usuario que ha iniciado sesión en el combobox "Seleccione ID Usuario"
    id_usuario_combobox = [widget for widget in tab_clientes.winfo_children() if isinstance(widget, ttk.Combobox)][0]
    id_usuario_combobox.set(user_logged_in_id)

    for widget in tab_clientes.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'
        elif isinstance(widget, tk.Button) and widget['text'] == "Cancelar":
            widget['state'] = 'normal'



def get_next_cliente_id():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(cliente_id) FROM clientes")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result[0] is None:
        return 1
    return result[0] + 1

def salvar_cliente():
    global modo_formulario_clientes  

    conn = conectar_db()
    cursor = conn.cursor()

    user_id_seleccionado = id_usuario_combobox.get()
    entries = [widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry)]
    
    cliente_id = entries[2].get()  
    nombre = entries[3].get()
    apellido_paterno = entries[4].get()
    apellido_materno = entries[5].get()

    values = [user_id_seleccionado, nombre, apellido_paterno, apellido_materno, cliente_id]  

    if modo_formulario_clientes == "nuevo":
        query = "INSERT INTO clientes (user_id, nombre, apellido_paterno, apellido_materno) VALUES (%s, %s, %s, %s)"
        values.pop()
    elif modo_formulario_clientes == "editar":
        query = "UPDATE clientes SET user_id=%s, nombre=%s, apellido_paterno=%s, apellido_materno=%s WHERE cliente_id=%s"
    else:
        messagebox.showerror("Error", "Modo desconocido.")
        return

    try:
        cursor.execute(query, tuple(values))
        conn.commit()

        if modo_formulario_clientes == "nuevo":
            messagebox.showinfo("Información", "Cliente guardado exitosamente.")
            
        elif modo_formulario_clientes == "editar":
            messagebox.showinfo("Información", "Cliente actualizado exitosamente.")
        
        for entry in entries:
            entry['state'] = 'readonly'

        for widget in tab_clientes.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
                widget['state'] = 'disabled'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Nuevo", "Cancelar"]:
                widget['state'] = 'normal'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar el cliente: {e}")

    actualizar_combobox_clientes()
    cursor.close()
    conn.close()


def editar_cliente():
    global modo_formulario_clientes 
    
    modo_formulario_clientes = "editar" 
    
    entries = [widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        if entry.grid_info()['row'] not in [0, 2]: 
            entry['state'] = 'normal'

    id_usuario_combobox = next(widget for widget in tab_clientes.winfo_children() if isinstance(widget, ttk.Combobox))
    id_usuario_combobox['state'] = 'normal'

    for widget in tab_clientes.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Salvar":
            widget['state'] = 'normal'

def remover_cliente():
    search_entry = next(widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    cliente_id_str = search_entry.get()

    answer = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar a este cliente?")
    
    if not answer:  
        return

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM clientes WHERE cliente_id = %s"
        cursor.execute(query, (cliente_id_str,))
        conn.commit()
        
        # Mensaje de éxito y reseteo de los widgets
        messagebox.showinfo("Información", "Cliente eliminado exitosamente.")
        search_entry.delete(0, tk.END)
        for widget in tab_clientes.winfo_children():
            if isinstance(widget, tk.Entry) and widget != search_entry:
                widget['state'] = 'normal'
                widget.delete(0, tk.END)
                widget['state'] = 'readonly'
            elif isinstance(widget, ttk.Combobox):
                widget['state'] = 'normal'
                widget.set('')
                widget['state'] = 'readonly'
            elif isinstance(widget, tk.Button) and widget['text'] in ["Cancelar", "Editar", "Remover"]:
                widget['state'] = 'disabled'

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al eliminar el cliente: {e}")

    cursor.close()
    conn.close()

def cancelar_cliente():
    global modo_formulario_clientes  
    
    modo_formulario_clientes = "none"  

    # Limpiar y deshabilitar todas las entradas
    entries = [widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry)]
    for entry in entries:
        entry.delete(0, tk.END)
        entry['state'] = 'disabled'

    # Habilitar solo la entrada "Ingrese ID a Buscar"
    id_buscar_entry = next(widget for widget in tab_clientes.winfo_children() if isinstance(widget, tk.Entry) and widget.grid_info()['row'] == 0)
    id_buscar_entry['state'] = 'normal'

    # Configurar el estado de los botones
    for widget in tab_clientes.winfo_children():
        if isinstance(widget, tk.Button):
            if widget['text'] in ["Nuevo", "Buscar"]:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'

    for widget in tab_clientes.winfo_children():
        if isinstance(widget, ttk.Combobox):
            widget.set('')  # Limpiar la selección del ComboBox
            widget['state'] = 'disabled'  # Deshabilitar el ComboBox

######################################################-------VISTA GENERAL-----------########################################################################


def obtener_datos(tabla):
    conn = conectar_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM {tabla}"
    cursor.execute(query)
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return datos

def mostrar_datos():
    opcion_seleccionada = vista_general_combobox.get()
    
    for widget in tab_vista_general.winfo_children():
        widget.destroy()

    vista_general_tab_layout()

    if opcion_seleccionada == "Clientes":
        columnas = ["cliente_id", "user_id", "nombre", "apellido_paterno", "apellido_materno"]
    elif opcion_seleccionada == "Usuarios":
        columnas = ["id", "username", "password", "role", "nombre", "apellido_paterno", "apellido_materno", "telefono", "direccion"]
    elif opcion_seleccionada == "Vehiculos":
        columnas = ["vehiculo_id", "cliente_id", "matricula", "marca", "modelo", "fecha"]
    elif opcion_seleccionada == "Piezas":
        columnas = ["pieza_id", "stock", "descripcion"]
    elif opcion_seleccionada == "Reparaciones":
        columnas = ["reparacion_id", "vehiculo_id", "pieza_id", "falla", "fecha_entrada", "fecha_salida", "cantidad_piezas"]

    tree = ttk.Treeview(tab_vista_general, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=65)
    tree.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

    datos = obtener_datos(opcion_seleccionada.lower())
    for fila in datos:
        tree.insert("", "end", values=fila)

def mostrar_datos_mecanico():
    opcion_seleccionada = vista_general_m_combobox.get()
    
    for widget in tab_vista_general_mecanico.winfo_children():
        widget.destroy()

    vista_general_mecanico_tab_layout()

    if  opcion_seleccionada == "Vehiculos":
        columnas = ["vehiculo_id", "cliente_id", "matricula", "marca", "modelo", "fecha","id_mecanico"]
    elif opcion_seleccionada == "Piezas":
        columnas = ["pieza_id", "stock", "descripcion"]
    elif opcion_seleccionada == "Reparaciones":
        columnas = ["reparacion_id", "vehiculo_id", "pieza_id", "falla", "fecha_entrada", "fecha_salida", "cantidad_piezas"]

    tree = ttk.Treeview(tab_vista_general_mecanico, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=65)
    tree.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

    datos = obtener_datos(opcion_seleccionada.lower())
    for fila in datos:
        tree.insert("", "end", values=fila)

def mostrar_datos_secretaria():
    opcion_seleccionada = vista_general_s_combobox.get()
    
    for widget in tab_vista_general_secretaria.winfo_children():
        widget.destroy()

    vista_general_secretaria_tab_layout()

    if opcion_seleccionada == "Clientes":
        columnas = ["cliente_id", "user_id", "nombre", "apellido_paterno", "apellido_materno"]
    elif opcion_seleccionada == "Vehiculos":
        columnas = ["vehiculo_id", "cliente_id", "matricula", "marca", "modelo", "fecha","id_mecanico"]


    tree = ttk.Treeview(tab_vista_general_secretaria, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=65)
    tree.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

    datos = obtener_datos(opcion_seleccionada.lower())
    for fila in datos:
        tree.insert("", "end", values=fila)
######################################################-------PESTAÑAS PRINCIPALES-----------########################################################################

def usuarios_tab_layout():
    tk.Label(tab_usuarios, text="Ingrese ID a Buscar").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    search_entry = tk.Entry(tab_usuarios)
    search_entry.grid(row=0, column=1, pady=10, padx=10, columnspan=2, sticky="we")
    tk.Button(tab_usuarios, text="Buscar", command=buscar_usuario).grid(row=0, column=3, pady=10, padx=10)

    labels = ["ID", "Nombre:", "Apellido Paterno", "Apellido Materno", "Telefono", "UserName:", "Direccion", "Password:"]
    add_labels_and_entries(tab_usuarios, labels, start_row=1, search_entry=search_entry)

    tk.Label(tab_usuarios, text="Perfil:").grid(row=7, column=2, pady=10, padx=10, sticky="e")
    perfil_combo = ttk.Combobox(tab_usuarios, values=["Admin", "Gerente", "Secretaria", "Mecanico"])
    perfil_combo.grid(row=7, column=3, pady=10, padx=10, sticky="we")

    add_action_buttons_usuarios(tab_usuarios, 10)

    configure_columns(tab_usuarios, [1, 3, 3, 1])

    add_padding(tab_usuarios)

def clientes_tab_layout():
    global id_usuario_combobox
    tk.Label(tab_clientes, text="Ingrese ID a Buscar").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tk.Entry(tab_clientes).grid(row=0, column=1, pady=10, padx=10, columnspan=2, sticky="we")
    tk.Button(tab_clientes, text="Buscar", command=buscar_cliente).grid(row=0, column=3, pady=10, padx=10)

    tk.Label(tab_clientes, text="Seleccione ID Usuario:").grid(row=1, column=0, pady=10, padx=10, sticky="e")
    id_usuario_combobox = ttk.Combobox(tab_clientes)
    id_usuario_combobox.grid(row=1, column=1, pady=10, padx=10, sticky="we")
    

    labels = ["Cliente ID", "Nombre:", "Apellido Paterno", "Apellido Materno"]
    add_labels_and_entries(tab_clientes, labels, start_row=2)

    add_action_buttons_clientes(tab_clientes, 6)

    configure_columns(tab_clientes, [1, 3, 3, 1])
    add_padding(tab_clientes)

def vehiculos_tab_layout():
    global id_cliente_combobox
    global id_mecanico_combobox

    tk.Label(tab_vehiculos, text="Ingrese ID a Buscar").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tk.Entry(tab_vehiculos).grid(row=0, column=1, pady=10, padx=10, columnspan=2, sticky="we")
    tk.Button(tab_vehiculos, text="Buscar", command=buscar_vehiculo).grid(row=0, column=3, pady=10, padx=10)

    tk.Label(tab_vehiculos, text="Seleccione ID Cliente:").grid(row=1, column=0, pady=10, padx=10, sticky="e")
    id_cliente_combobox = ttk.Combobox(tab_vehiculos, name="cliente_combobox_1")
    id_cliente_combobox.grid(row=1, column=1, pady=10, padx=10, sticky="we")

    tk.Label(tab_vehiculos, text="Seleccione ID Mecanico:").grid(row=2, column=0, pady=10, padx=10, sticky="e")
    id_mecanico_combobox = ttk.Combobox(tab_vehiculos, name="mecanico_combobox")
    id_mecanico_combobox.grid(row=2, column=1, pady=10, padx=10, sticky="we")

    labels = ["Vehiculo ID", "Matricula:", "Marca", "Modelo", "Fecha"]
    add_labels_and_entries(tab_vehiculos, labels, start_row=3)

    add_action_buttons_vehiculos(tab_vehiculos, 8)

    configure_columns(tab_vehiculos, [1, 3, 3, 1])
    add_padding(tab_vehiculos)



def reparaciones_tab_layout():
    global id_vehiculo_combobox
    global id_pieza_combobox

    tk.Label(tab_reparaciones, text="Ingrese ID a Buscar").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tk.Entry(tab_reparaciones).grid(row=0, column=1, pady=10, padx=10, columnspan=2, sticky="we")
    tk.Button(tab_reparaciones, text="Buscar", command=buscar_reparacion).grid(row=0, column=3, pady=10, padx=10)

    tk.Label(tab_reparaciones, text="Vehiculo ID").grid(row=1, column=0, pady=10, padx=10, sticky="e")
    id_vehiculo_combobox = ttk.Combobox(tab_reparaciones,name="vehiculo_combobox")
    id_vehiculo_combobox.grid(row=1, column=1, pady=10, padx=10,columnspan= 2, sticky="we")

    tk.Label(tab_reparaciones, text="Pieza ID").grid(row=2, column=0, pady=10, padx=10, sticky="e")
    id_pieza_combobox = ttk.Combobox(tab_reparaciones, name="pieza_combobox")
    id_pieza_combobox.grid(row=2, column=1, pady=10, padx=10, columnspan= 2, sticky="we")

    labels = ["Reparación ID", "Fecha Entrada", "Fecha Salida", "Falla", "Cantidad Piezas"]
    add_labels_and_entries(tab_reparaciones, labels, start_row=3)

    add_action_buttons_reparaciones(tab_reparaciones, 9)

    configure_columns(tab_reparaciones, [1, 2, 1, 2, 2])
    add_padding(tab_reparaciones)
    

def piezas_tab_layout():
    tk.Label(tab_piezas, text="Ingrese ID a Buscar").grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tk.Entry(tab_piezas).grid(row=0, column=1, pady=10, padx=10, columnspan=2, sticky="we")
    tk.Button(tab_piezas, text="Buscar", command=buscar_pieza).grid(row=0, column=3, pady=10, padx=10)

    # Etiquetas y campos de entrada para detalles de la pieza
    labels = ["Pieza ID:", "Descripción:", "Stock:"]
    add_labels_and_entries(tab_piezas, labels, start_row=2)
    add_action_buttons_piezas(tab_piezas, 5)
    configure_columns(tab_piezas, [1, 2, 1, 2, 2])
    add_padding(tab_piezas)

def vista_general_tab_layout():
    global vista_general_combobox
    tk.Label(tab_vista_general, text="Seleccione una opción:").grid(row=0, column=0, pady=10, padx=10, sticky="e")

    opciones = ["Clientes", "Vehiculos", "Piezas", "Reparaciones", "Usuarios"]
    vista_general_combobox = ttk.Combobox(tab_vista_general, values=opciones)
    vista_general_combobox.grid(row=0, column=1, pady=10, padx=10, sticky="we")

    tk.Button(tab_vista_general, text="Mostrar", command=mostrar_datos).grid(row=1, column=0, pady=10, padx=10)

def vista_general_mecanico_tab_layout():
    global vista_general_m_combobox
    tk.Label(tab_vista_general_mecanico, text="Seleccione una opción:").grid(row=0, column=0, pady=10, padx=10, sticky="e")

    opciones = ["Vehiculos", "Piezas", "Reparaciones"]
    vista_general_m_combobox = ttk.Combobox(tab_vista_general_mecanico, values=opciones)
    vista_general_m_combobox.grid(row=0, column=1, pady=10, padx=10, sticky="we")

    tk.Button(tab_vista_general_mecanico, text="Mostrar", command=mostrar_datos_mecanico).grid(row=1, column=0, pady=10, padx=10)

def vista_general_secretaria_tab_layout():
    global vista_general_s_combobox
    tk.Label(tab_vista_general_secretaria, text="Seleccione una opción:").grid(row=0, column=0, pady=10, padx=10, sticky="e")

    # ComboBox con las opciones
    opciones = ["Clientes","Vehiculos"]
    vista_general_s_combobox = ttk.Combobox(tab_vista_general_secretaria, values=opciones)
    vista_general_s_combobox.grid(row=0, column=1, pady=10, padx=10, sticky="we")

    tk.Button(tab_vista_general_secretaria, text="Mostrar", command=mostrar_datos_secretaria).grid(row=1, column=0, pady=10, padx=10)

######################################################-------VENTANA PRINCIPAL -----------########################################################################

window = tk.Tk()
window.title("Sistema Taller Mecanico")
window.geometry('631x443')

notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Centrar la ventana en la pantalla
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width / 2) - (631 / 2)
y = (screen_height / 2) - (443 / 2)

window.geometry("+%d+%d" % (x, y))

# Hacer que la ventana no sea redimensionable
window.resizable(False, False)
tab_login = ttk.Frame(notebook)
notebook.add(tab_login, text="Login")

tk.Label(tab_login, text="Nombre de usuario").pack()
entry_username = tk.Entry(tab_login)
entry_username.pack()

tk.Label(tab_login, text="Contraseña").pack()
entry_password = tk.Entry(tab_login, show="*")
entry_password.pack()

tk.Button(tab_login, text="Iniciar sesión", command=login).pack()
tk.Button(tab_login, text="Cerrar Sesión", command=logout).pack()

# Pestañas de la ventana
tab_usuarios = ttk.Frame(notebook)
tab_clientes = ttk.Frame(notebook)
tab_vehiculos = ttk.Frame(notebook)
tab_reparaciones = ttk.Frame(notebook)
tab_piezas = ttk.Frame(notebook)
tab_vista_general = ttk.Frame(notebook)
tab_vista_general_mecanico = ttk.Frame(notebook)
tab_vista_general_secretaria = ttk.Frame(notebook)


window.mainloop()
