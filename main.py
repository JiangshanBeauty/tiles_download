
from flask import Flask, Response, jsonify, render_template, request
from collections import namedtuple, Counter


Tile = namedtuple('Tile', ['x', 'y', 'z'])
tile_counter = Counter()

app = Flask(__name__)

@app.route("/tile")
def tile():
    x = int(request.args['x'])
    y = int(request.args['y'])
    z = int(request.args['z'])
    t = Tile(x, y, z)
    try:
        with open('C:/Users/mzy/ideaproject/tiles_download/tilefile/%s/%s/%s.png'%(z,x,y), 'rb') as f:
            image = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Tile not found'})
    except Exception as e:
        return jsonify({'error': str(e)})
    tile_counter[t] += 1
    return Response(image, mimetype='image/jpeg')

@app.route('/', methods=['GET'])
def map():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True, threaded=True)
