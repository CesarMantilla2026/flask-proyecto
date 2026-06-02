from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'
DATABASE = 'database.db'

def consultar_db(query, args=(), fetchone=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    resultado = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.close()
    return resultado

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = consultar_db("SELECT username, nombre FROM usuarios WHERE username = ? AND password = ?", (username, password), fetchone=True)
        
        if usuario:
            session['usuario'] = usuario[0]
            session['nombre'] = usuario[1]
            return redirect(url_for('principal'))
        else:
            error = "Credenciales incorrectas. Intente de nuevo."
            
    return render_template('login.html', error=error)

@app.route('/principal')
def principal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('principal.html', nombre=session['nombre'])

@app.route('/buscador')
def buscador():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('buscador.html')

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    if 'usuario' not in session:
        return jsonify({"error": "No autorizado"}), 401
        
    datos = request.get_json()
    codigo = datos.get('codigo', '').upper()
    
    prod = consultar_db("SELECT codigo, nombre, descripcion, precio, stock, categoria FROM productos WHERE codigo = ?", (codigo,), fetchone=True)
    
    if prod:
        return jsonify({
            "codigo": prod[0],
            "nombre": prod[1],
            "descripcion": prod[2],
            "precio": prod[3],
            "stock": prod[4],
            "categoria": prod[5]
        }), 200
    else:
        return jsonify({"error": "Producto no encontrado"}), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)