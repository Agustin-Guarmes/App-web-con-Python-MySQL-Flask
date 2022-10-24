from flask import Flask             #impoto el framework
from flask import render_template,request,redirect,url_for, flash 
"""render_template permite mostrar los templates, es decir , la pagina del employees, para editar, para crear los registros
request (solicitud) permite obtener la info del formulario, pide informacion
redirect me permite volver a la URL de donde vine, una vez eliminado el registro
url_for (que lleva dos parametros) permite acceder a un metodo de app.py desde un template
flash genera mensajes informativos (para validar), el vual necesita un secret key
"""
from flaskext.mysql import MySQL    #permite conectarme con la base de datos de MySQL
from datetime import datetime       #modulo q nos permite perzonalizar el nombre de la foto
import os                           #permite trabajar con archivos y carpetas
from flask import send_from_directory   #permite buscar si el archivo esta en la carpeta

#configuracion de la BD
app = Flask(__name__)               #para crear la app de Flask
app.secret_key="ClaveSecreta"       #no se utiliza, pero es necesaria para flash
mysql = MySQL()                     #objeto mysql de la calss MySQL
app.config['MYSQL_DATABASE_HOST']='localhost'       #configurar host, contraseña y BD para asi saber que datos tenemos en la configuracion. Se crea la referencia del host para que despues se pueda conectar a la BD de MySQL utilizando el localhost
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''            #lo dejamos sin contraseña
app.config['MYSQL_DATABASE_BD']='sistema_proyecto'  #nombre de la base de datos
mysql.init_app(app)                                 #esta es la conexion con los datos e inicia la aplicacion

CARPETA= os.path.join('uploads')    #el metodo join te permite unir uno o mas componentes de una ruta, es decir, concatena los componentes de una ruta con un separador de directorio ("/") y luego pongo el nombre de la carpeta
app.config['CARPETA']=CARPETA       #indico que guardo esa ruta de la carpeta uploads

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)   #este metodo me dirige a la carpeta uploads a traves de la variable carpeta y me muestra la foto guarda la variable nombreFoto

#conexion de la BD
@app.route('/')
def index():
    return render_template('empleados/index.html')

@app.route('/employees')                     #para que el usuario empiece en la raiz cuando comience a trabajar
def employees():                        #es para que el usuario pueda ver el employees.html creado
    sql = "SELECT * FROM `sistema_proyecto`.`empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()          #permite procesasr de manera individual las filas que devuelve el sistema de BD. Almacena lo que ejecute en connect
    cursor.execute(sql)             #ejecuta la sentencia sql
    
    empleados=cursor.fetchall()     #fetchall recupera todas las filas del resultado de la consulta, devuelve las filas como una lista de tuplas
    #print(empleados)                era para ver si funcionaba, lo veo en la terminal despues de actualizar la pag
    
    conn.commit()
    return render_template('empleados/employees.html', empleados=empleados)  #retorna la plantilla html + la lista de empleados

@app.route('/destroy/<int:id>')     #recibe como parametro el id del egistro que vamos a eliminar (donde le digo que es un tipo de dato entero)
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM `sistema_proyecto`.`empleados` WHERE id=%s",id)    #ejecuto la consulta para traer el dato, es decir, la foto
    fila= cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))  #la elimino
    cursor.execute("DELETE FROM `sistema_proyecto`.`empleados` WHERE id=%s", (id))  #va a ser el id que le pasamos como parametro. Inserción de valores reemplazados por los que les paso. Elimino la sentencia de todo el registro de la persona
    conn.commit()
    return redirect('/employees')            #retorno al lugar de donde vengo

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `sistema_proyecto`.`empleados` WHERE id=%s", (id)) #necesito seleccionar para despues editarlo
    empleados=cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados=empleados)   #le digo que me retorne el formulario de edit, pero necesito traer los datos de los empleados

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']   #traigo los datos desde el formulario
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']
    sql = "UPDATE `sistema_proyecto`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;" #esta sentencia actualiza el nombre y el correo
    datos=(_nombre,_correo,id)
    
    conn = mysql.connect()  #hago la conexion 
    cursor = conn.cursor()  #cursor es un obj que puede ejecutar operaciones como sentencias SQL
    
    now= datetime.now()     #a la foto nueva que se agrega traemos el tiempo, renombramos la foto y hacer el save
    tiempo= now.strftime("%Y%H%M%S")
    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        cursor.execute("SELECT foto FROM `sistema_proyecto`.`empleados` WHERE id=%s", id)   #recupera la foto y actualiza solamente ese campo de foto, para lo que necesito una instruccion SQL
        fila= cursor.fetchall()     #guardo los datos en la variable fila, porque necesito borrar la foto
        
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))  #os me permite eliminar el archivo (para este caso el que esta en la carpeta upload). Lo que tenemos que eliminar lo traemos con fila y las dos posiciones (fila 0, col 0 --> id)
        cursor.execute("UPDATE `sistema_proyecto`.`empleados` SET foto=%s WHERE id=%s", (nuevoNombreFoto, id))   #ejecutamos la actualizacion de la nueva foto
        conn.commit()
        
    cursor.execute(sql,datos)
    conn.commit()           #cierro la conexion
    
    return redirect('/employees')    #para volver a donde estaba despues de la actualizacion

#referencia a create.html
@app.route('/create')
def create():                       #la funcion permite mostrar la vista html
   return render_template('empleados/create.html')  #retorna la plantilla html

@app.route('/store', methods=['POST']) #routep + tab, se hace solo y lo edito (tiene post como el form)
def storage():                          #lo uso parra guardar la informacion
    _nombre = request.form['txtNombre'] #_ xq es atributo privado, request pide al form y entre corchetes de donde saco la info, es decir, el nombre del campo (es lo mismo q .value en JS)
    _correo = request.form['txtCorreo'] #recupero del formulario el dato del correo
    _foto = request.files['txtFoto']    #cambia form por file, ver el html
    
    if _nombre == '' or _correo == '' or _foto =='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))

    now= datetime.now()                #la variable toma la fecha y hora de subida de la foto
    tiempo= now.strftime("%Y%H%M%S")   #pasamos el objeto date a str (como tostring), donde agregamos como parametros %Y año, hs, min y seg

    if _foto.filename!='':             #para ver si la foto no quedo vacia
        nuevoNombreFoto=tiempo+_foto.filename   #variable que se le concatena el tiempo + el nombre
        _foto.save("uploads/"+nuevoNombreFoto)    #guardamos la foto en la carpeta uploads con el nombre del archivo

    sql = "INSERT INTO `sistema_proyecto`.`empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"  #con %s reemplazo los valores fijos por los que se ingresan en el form
    datos=(_nombre,_correo,nuevoNombreFoto)     #vincula la tupla con los %s (cambia _foto.filename porque ahora se llama nuevoNombreFoto)
    
    conn = mysql.connect()          #hace la conexion
    cursor = conn.cursor()          #permite procesasr de manera individual las filas que devuelve el sistema de BD. Almacena lo que ejecute en connect
    cursor.execute(sql, datos)      #ejecuta la sentencia sql
    conn.commit()                   #cierra la conexion
    return redirect('/employees')            #retorna al template

if __name__=='__main__':            #if que requiere py para empezar a trabajar con la app
    app.run(debug=True)             #en modo debug activa al depurador