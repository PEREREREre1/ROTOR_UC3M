from flask import Flask, request, render_template, jsonify, redirect, url_for

import tracker
import rot2prog
import lector_archivos_celestrak


app = Flask(__name__)

@app.route('/')
#Aqui mostramos los argumentos al iniciar la pantalla
def main_page():
    az, el = "45", "32"
    satellite_def = lector_archivos_celestrak.get_satellite("NOAA 15",lector_archivos_celestrak.get_satellites())
    norad_id = lector_archivos_celestrak.get_ID()
    names_satellites = lector_archivos_celestrak.get_list_names()
    return render_template("index.html", az=az, el=el, satellite_info=satellite_def, norad_n2yo = norad_id,names = names_satellites)


@app.route('/api/get_pos')
def get_pos():
    """Get the current azimuth and elevation of the rotator."""
    try:
        az, el = rot2prog.get_pos()
        return jsonify({'az': az, 'el': el})
    except:
        return jsonify({'error': 'error'}), 500

@app.route('/api/set_pos', methods=['POST'])
def set_pos():
    """Set the rotator to the given azimuth and elevation.

    POST only.

    (Exit code 0 means the command was sent to the controller.
    It does not mean the rotator was actually set to the values given.)
    """
    try:
        az = float(request.form['az'])
        el = float(request.form['el'])
    except:
        return jsonify({'error': 'error'}), 400 # bad input
    
    try:
        return jsonify({'exit_code': rot2prog.set_pos(az, el)})
    except:
        return jsonify({'error': 'error'}), 500



@app.route('/api/set_sat_name', methods=['GET','POST'])
def set_sat_name():
    if request.method == "POST":    
        try:
            satelite_def = str(request.form['satelite'])
        except:
            return jsonify({'error'}), 400 # bad input
        try:
            print("Renderiza")
            satellite_def = lector_archivos_celestrak.set_satellite(satelite_def,lector_archivos_celestrak.get_satellites())
            norad_id = lector_archivos_celestrak.get_ID()
            names_satellites = lector_archivos_celestrak.get_list_names()
            return render_template("index.html", satellite_info=satellite_def,norad_n2yo = norad_id,names = names_satellites)
        except:
            return jsonify({'error'}), 500
    else:
        try:
            print(lector_archivos_celestrak.get_coordinates())
            return jsonify(lector_archivos_celestrak.get_coordinates())
        except:
            return jsonify({'error'}), 50
"""
@app.route('/api/selec_sat_name', methods=['POST'])
def selec_sat_name():
    try:
        satelite_def = str(request.form['selection'])
    except:
        return jsonify({'error'}), 400 # bad input
    try:
        satellite_def = lector_archivos_celestrak.set_satellite(satelite_def,lector_archivos_celestrak.get_satellites())
        names_satellites = lector_archivos_celestrak.get_list_names()
        return render_template("index.html", satellite_info=satellite_def,names = names_satellites)
    except:
        return jsonify({'error'}), 500
"""
@app.route('/api/get_pases')
def get_pases():
    try:
        print("aqui"+str(lector_archivos_celestrak.get_pases()))
        return jsonify(lector_archivos_celestrak.get_pases())
    except:
        print("aqui2"+lector_archivos_celestrak.get_pases())
        return jsonify({'error': 'error'}), 500



@app.route('/api/seguir_pase',methods=['POST'])
def seguir_pase():
    try:
        index_def = int(request.form['index_def'])
        satelite_def = str(request.form['satelite_def'])
        print(index_def)
    except:
        return jsonify({'error': 'error'}), 400 # bad input
    
    try:
        return jsonify(lector_archivos_celestrak.hilo_espera(index_def,satelite_def))
    except:
        return jsonify({'error': 'error'}), 500
    



if __name__ == '__main__':
    app.run(debug=True, port=5000)
