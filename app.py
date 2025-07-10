from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from cs50 import SQL
import pandas as pd
from datetime import datetime
import os
from helpers import login_required
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect


os.environ["TERM"] = "dumb"

# Configure application
app = Flask(__name__, static_folder='./statics')

csrf = CSRFProtect(app)

# Configuración de rate limiting (ej: 5 intentos por minuto)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])

# Ruta al archivo de log
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')

# Crear directorio si no existe
if not os.path.exists(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))

# Crear un handler que escriba en un archivo de log y limite su tamaño (rotación)
handler = RotatingFileHandler(log_path, maxBytes=10000000, backupCount=3)
handler.setLevel(logging.DEBUG)

# Crear un formateador de logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Agregar el handler a la aplicación Flask
app.logger.addHandler(handler)

# Configurar el nivel de logging
app.logger.setLevel(logging.DEBUG)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./statics/images"

# Configure session to use filesystem (instead of signed cookies)
app.config['SECRET_KEY'] = 'QlKo45986PplOkskd/&%?0Kkj@klsoLSOSodsosd'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_FILE_DIR'] = './tmp/flask_session'
Session(app)

db = SQL("sqlite:///database.db")


@app.route("/", methods=["GET", "POST"])
def index():
    
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get the values of the form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        nivel = request.form.get("nivel")
        #print(nivel)
        level = 0

        # Username is empty? Username alredy exist in the table users?
        if not username or db.execute("SELECT * FROM users WHERE username = ?", username) or password != confirmation or not password:
            return render_template("error.html")

        if nivel == "administrador":
            level = 794652315648
        if nivel == "boss":
            level = 794652315647

        # Save the new user in the table with hashed password
        db.execute("INSERT INTO users (username, password, accesslevel) VALUES (?, ?, ?)",
                   username, generate_password_hash(password), level)
        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Validación básica
        if not username or not password:
            return render_template("error.html")

        # Consulta segura
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return render_template("error.html")

        # Configuración de sesión segura
        session.permanent = False  # La sesión expira al cerrar el navegador
        session["user_id"] = rows[0]["id"]
        session["user_level"] = rows[0]["accesslevel"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/minegocio", methods=["GET", "POST"])
@login_required
def minegocio():
    return render_template("minegocio.html", nombre="Mi Negocio")


@app.route("/cargadiaria", methods=["GET", "POST"])
@login_required
def cargadiaria():
    return render_template("cargadiaria.html", nombre="Mi Negocio")


@app.route("/presupuestos", methods=["GET", "POST"])
@login_required
def presupuestos():
    return render_template("presupuestos.html", nombre="Mi Negocio")


@app.route("/listaprecios", methods=["GET", "POST"])
@login_required
def listaprecios():
    return render_template("listaprecios.html", nombre="Mi Negocio")


@app.route("/stock", methods=["GET", "POST"])
@login_required
def stock():
    return render_template("stock.html", nombre="Control de stock")


@app.route("/compras", methods=["GET", "POST"])
@login_required
def compras():
    return render_template("compras.html", nombre="Compras")


@app.route("/gastos", methods=["GET", "POST"])
@login_required
def gastos():
    return render_template("gastos.html", nombre="Gastos")


@app.route("/formulario", methods=["GET", "POST"])
@login_required
def formulario():

    encargadas = db.execute("SELECT * FROM empleados")
    locales = db.execute("SELECT * FROM locales")
    # Formulario de carga de cierre de caja.
    if request.method == "POST":
        Hora = request.form.get("startDate")
        Hora = datetime.strptime(Hora, "%Y-%m-%d").strftime("%d-%m-%Y")
        Local = request.form.get("nombrelocal")
        EncargadaID = request.form.get("nombreencargada")
        Turno = request.form.get("turno")
        VisaNombre1 = request.form.get("nombrevisa1")
        VisaNombre2 = request.form.get("nombrevisa2")
        VisaNombre3 = request.form.get("nombrevisa3")
        VisaNombre4 = request.form.get("nombrevisa4")
        VisaImporte1 = request.form.get("importevisa1")
        VisaImporte2 = request.form.get("importevisa2")
        VisaImporte3 = request.form.get("importevisa3")
        VisaImporte4 = request.form.get("importevisa4")
        QrNombre = request.form.get("nombreqr")
        QrImporte = request.form.get("importeqr")
        TotalPosnet = request.form.get("totalposnet")
        TransferenciasText = request.form.get("transferenciastext")
        Transferencias = request.form.get("transferencias")
        PedidosYaText = request.form.get("pedidosyatext")
        PedidosYa = request.form.get("pedidosya")
        Cantidad20m = request.form.get("cantidad20m")
        Cantidad10m = request.form.get("cantidad10m")
        Cantidad2m = request.form.get("cantidad2m")
        Cantidad1m = request.form.get("cantidad1m")
        Cantidad500 = request.form.get("cantidad500")
        Cantidad200 = request.form.get("cantidad200")
        Cantidad100 = request.form.get("cantidad100")
        Cantidad50 = request.form.get("cantidad50")
        Cantidad20 = request.form.get("cantidad20")
        Cantidad10 = request.form.get("cantidad10")
        Total20m = request.form.get("total20m")
        Total10m = request.form.get("total10m")
        Total2m = request.form.get("total2m")
        Total1m = request.form.get("total1m")
        Total500 = request.form.get("total500")
        Total200 = request.form.get("total200")
        Total100 = request.form.get("total100")
        Total50 = request.form.get("total50")
        Total20 = request.form.get("total20")
        Total10 = request.form.get("total10")
        TotalEfectivo = request.form.get("totalefectivo")
        Egresos = request.form.get("egresos")
        TotalEgresos = request.form.get("totalegresos")
        EntregaEfectivo = request.form.get("entregaefectivo")
        EntregaPosnet = request.form.get("entregaposnet")
        TotalEfectivoSistema = request.form.get("totalefectivosistema")
        TotalPosnetSistema = request.form.get("totalposnetsistema")
        SobrantEfectivo = request.form.get("sobranteefectivo")
        SobrantePosnet = request.form.get("sobranteposnet")
        FaltanteEfectivo = request.form.get("faltanteefectivo")
        FaltantePosnet = request.form.get("faltanteposnet")
        TotalCierre = request.form.get("totalcierre")
        TotalSistema = request.form.get("totalsistema")
        TotalDescuentosCierre = request.form.get("totaldescuentoscierre")
        TotalDescuentosSistema = request.form.get("totaldescuentossistema")
        Observaciones = request.form.get("observaciones")

        resultado = db.execute("SELECT nombre, apellido FROM empleados WHERE id = ?", (EncargadaID,))
        NombreEncargada = f"{resultado[0]['nombre']} {resultado[0]['apellido']}"
        print(NombreEncargada)

        try:
            # Insert values in the database
            db.execute("INSERT INTO formulario (fecha, nombre_encargada, turno, nombrevisa1, nombrevisa2, nombrevisa3, nombrevisa4, \
                    importevisa1, importevisa2, importevisa3, importevisa4, nombreqr, importeqr, totalposnet, transferencias_text, \
                    transferencias, pedidosya_text, pedidosya, cantidad20m, cantidad10m, cantidad2m, cantidad1m, cantidad500, cantidad200, \
                    cantidad100, cantidad50, cantidad20, cantidad10, total20m, total10m, total2m, total1m, total500, total200, total100, \
                    total50, total20, total10, totalefectivo, egresos, totalegresos, entregaefectivo, entregaposnet, totalefectivosistema, \
                    totalposnetsistema, sobranteefectivo, sobranteposnet, faltanteefectivo, faltanteposnet, totalcierre, totalsistema, \
                    totaldescuentoscierre, totaldescuentossistema, observaciones, local, checkeado, idencargada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    Hora, NombreEncargada, Turno, VisaNombre1, VisaNombre2, VisaNombre3, VisaNombre4, VisaImporte1, VisaImporte2,
                    VisaImporte3, VisaImporte4, QrNombre, QrImporte, TotalPosnet, TransferenciasText, Transferencias, PedidosYaText,
                    PedidosYa, Cantidad20m, Cantidad10m, Cantidad2m, Cantidad1m, Cantidad500, Cantidad200, Cantidad100, Cantidad50,
                    Cantidad20, Cantidad10, Total20m, Total10m, Total2m, Total1m, Total500, Total200, Total100, Total50, Total20, Total10,
                    TotalEfectivo, Egresos, TotalEgresos, EntregaEfectivo, EntregaPosnet, TotalEfectivoSistema, TotalPosnetSistema,
                    SobrantEfectivo, SobrantePosnet, FaltanteEfectivo, FaltantePosnet, TotalCierre, TotalSistema, TotalDescuentosCierre,
                    TotalDescuentosSistema, Observaciones, Local, 0, EncargadaID)
            
            return render_template("formulariocargado.html", type="Formulario cargado")
        
        except:
            return render_template("error.html", style="Error") 

    return render_template("formulario.html",encargadas=encargadas, locales=locales, type="Formulario")


@app.route("/visualizacion")
@login_required
def visualizacion():

    try:
        cajas = db.execute("SELECT * FROM formulario ORDER BY substr(fecha, 7, 4) || '-' || substr(fecha, 4, 2) || '-' || substr(fecha, 1, 2) ASC")
        encargadas = db.execute("SELECT * FROM empleados")
        locales = db.execute("SELECT * FROM locales")
                   
    except:
        return render_template("error.html", style="Error") 

    return render_template("visualizacion.html", cajas=cajas, encargadas=encargadas, locales=locales, type="Cierres de Caja")


@app.route("/filtrarvisualizacion")
@login_required
def filtrarvisualizacion():

    mes = request.args.get("mes")
    anio = request.args.get("anio")
    local = request.args.get("local")
    encargada = request.args.get("idencargada")
    params = []

    try:
        query = "SELECT * FROM formulario WHERE 1=1"
        if mes:
            query += " AND (strftime('%m', substr(fecha, 7, 4) || '-' || substr(fecha, 4, 2) || '-' || substr(fecha, 1, 2))) = ?"
            params.append(mes)
            #params += (f"{mes}")
        
        if anio:
            query += " AND SUBSTR(fecha, 7, 4) = ?"
            params.append(anio)

        if local:
            query += " AND local = ?"
            params.append(local)

        if encargada:
            query += " AND idencargada = ?"
            params.append(encargada)

        query += " ORDER BY substr(fecha, 7, 4) || '-' || substr(fecha, 4, 2) || '-' || substr(fecha, 1, 2) ASC"
    
        cajas = db.execute(query, *params)
        encargadas = db.execute("SELECT * FROM empleados")
        locales = db.execute("SELECT * FROM locales")
    
        return render_template("visualizacion.html", cajas=cajas, encargadas=encargadas, locales=locales, type="Cierres de Caja")

    except:
        return render_template("error.html", type="ERROR")


@app.route("/cargarencargada", methods=["GET", "POST"])
@login_required
@csrf.exempt
def cargarencargada():

    locales = db.execute("SELECT * FROM locales")

    try:
        if request.method == "POST":
            Nombre = request.form.get("nombre")
            Apellido = request.form.get("apellido")
            Local = request.form.get("local")
            Bonodecaja = request.form.get("bonodecaja")

            db.execute("INSERT INTO empleados (nombre, apellido, local, bonodecaja) VALUES (?, ?, ?, ?)", Nombre, Apellido, Local, Bonodecaja)

            return render_template("formulariocargado.html", type="Carga exitosa")
    except:
        return render_template("error.html", style="Error") 
    

    return render_template("cargarencargada.html", locales=locales, type="Nueva encargada")


@app.route("/modificarencargada", methods=["GET", "POST"])
@login_required
@csrf.exempt
def modificarencargada():

    encargadas = db.execute("SELECT * FROM empleados")
    locales = db.execute("SELECT * FROM locales")
    idencargada = request.args.get("idencargada")
    
    encargadaseleccionada = [{"nombre":"-", "apellido":"-", "local":"-", "bonodecaja":"-"}]

    try:
        if idencargada:
            encargadaseleccionada = db.execute("SELECT * FROM empleados WHERE id = ?", idencargada)

        if request.method == "POST":   
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            local = request.form.get("local")
            bonodecaja = request.form.get("bonodecaja")
            idencargada = request.form.get("encid")

            if nombre:
                    db.execute("UPDATE empleados SET nombre = ? WHERE id = ?", nombre, idencargada)
            
            if apellido:
                    db.execute("UPDATE empleados SET apellido = ? WHERE id = ?", apellido, idencargada)

            if local:
                    db.execute("UPDATE empleados SET local = ? WHERE id = ?", local, idencargada)
            
            if bonodecaja:
                    db.execute("UPDATE empleados SET bonodecaja = ? WHERE id = ?", bonodecaja, idencargada)
    except:
        return render_template("error.html", style="Error") 

    return render_template("modificarencargada.html", locales=locales, encargadaseleccionada=encargadaseleccionada, encargadas=encargadas, type="Modificar o eliminar encargada")


@app.route("/eliminarencargada", methods=["GET", "POST"])
@login_required
@csrf.exempt
def eliminarencargada():

    if request.method == "POST":
        encargadaid = request.form.get("encid")

        if encargadaid:
            try:
                #encargada = db.execute("SELECT * FROM empleados WHERE id = ?", encargadaid)
                db.execute("DELETE FROM empleados WHERE id = ?", encargadaid)
            except:
                return render_template("error.html", style="Error")     
            
        
        encargadas = db.execute("SELECT * FROM empleados")
        locales = db.execute("SELECT * FROM locales")
        
        encargadaseleccionada = [{"nombre":"-", "apellido":"-", "local":"-", "bonodecaja":"-"}]

        return render_template("modificarencargada.html", locales=locales, encargadaseleccionada=encargadaseleccionada, encargadas=encargadas, type="Modificar o eliminar encargada")
    

@app.route("/detallescaja", methods=["GET", "POST"])
@login_required
@csrf.exempt
def detallescaja():

    idcaja=request.form.get("idcaja")
    try:
        caja = db.execute("SELECT * FROM formulario WHERE id = ?", idcaja)
    except:
        return render_template("error.html", style="Error")  
    
    return render_template("detallescaja.html", caja=caja, type="Detalles de caja")


@app.route("/bonosdecaja", methods=["GET", "POST"])
@login_required
@csrf.exempt
def bonosdecaja():

    bono = [{'bonodecaja':0}]
    encargadas = db.execute("SELECT * FROM empleados")
    idencargada = request.args.get("idencargada")
    mes = request.args.get("mes")
    cajafiltrada={}

    if idencargada and mes:
        try:
            bono = db.execute("SELECT * FROM empleados WHERE id = ?", idencargada)
            cajafiltrada = db.execute("SELECT * FROM formulario WHERE idencargada = ? AND strftime('%m', substr(fecha, 7, 4) || '-' || substr(fecha, 4, 2) || '-' || substr(fecha, 1, 2)) = ?", idencargada, mes)
        except:
            return render_template("error.html", type="Error")
    elif idencargada:
        try:
            bono = db.execute("SELECT * FROM empleados WHERE id = ?", idencargada)
            cajafiltrada = db.execute("SELECT * FROM formulario WHERE idencargada = ?", idencargada)
        except:
            return render_template("error.html", type="Error")

    return render_template("bonosdecaja.html", caja=cajafiltrada, encargadas=encargadas, bono=bono, type="Bonos de caja")


@app.route("/checkdecaja", methods=["GET", "POST"])
@login_required
@csrf.exempt
def checkdecaja():

    if request.method == "POST":
        idcaja = request.form.get("idcaja")

        if idcaja:
            try:
                caja = db.execute("SELECT * FROM formulario WHERE id = ?", idcaja)
                return render_template("checkdecaja.html", caja=caja, type="Check de caja")
            except:
                return render_template("error.html", style="Error")     
    
    return render_template("checkdecaja.html", caja=caja, type="Detalles de caja")
    

@app.route("/guardarcajacheckeada", methods=["GET", "POST"])
@login_required
@csrf.exempt
def guardarcajacheckeada():

    if request.method == "POST":
        idcaja = request.form.get("idcaja")
        totalcheckeado = request.form.get("diferenciacheckeada")
        try:
            if totalcheckeado:
                db.execute("UPDATE formulario SET totalcheckeado = ?, checkeado = ? WHERE id = ?", totalcheckeado, 1, idcaja)

                return render_template("formulariocargado.html")
        except:
            return render_template("error.html")
    
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)