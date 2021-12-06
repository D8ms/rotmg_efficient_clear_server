from flask import Flask, session, request
import json
import redis


app = Flask(__name__)
r = redis.Redis('localhost',charset="utf-8", decode_responses=True)

def fixedTemplate():
    data = {}
    data['server'] = "..."
    data['mapIdx'] = 0
    for i in range(128):
        data[i] = 0
    return data

def groupId():
    return "MUG"

@app.route("/<lobby>", methods=["GET", "PUT", "POST"])
def derp(lobby):
    if request.method == "POST":
        print("HERE")
        try:
            data = request.get_json(force=True)
        except Exception as e:
            print("FUCK", e)
            data = {}
        print("POSTED DATA", data)
        d = fixedTemplate()
        for key in data.keys():
            d[key] = data[key]
        for key in d.keys():
            r.hset(lobby, key, d[key])
        return "new lobby set"

    if request.method == "PUT":
        data = request.get_json(force=True)
        print("PUT DATA", data, type(data))
        if r.exists(lobby):
            clientMapIdx = data.pop('mapIdx')
            clientServer = data.pop('server')
            serverMapIdx = r.hget(lobby, "mapIdx")
            if clientMapIdx != serverMapIdx:
                return "lobby existed, did not update though"
            for k in data.keys():
                v = data[k]
                r.hset(lobby, k, v)
                r.expire(lobby, 1800)
            return "lobby existed"
        else:
            d = fixedTemplate()
            for k in data.keys():
                v = data[k]
                d[k] = v
            for key in d.keys():
                r.hset(lobby, key, d[key])
            r.expire(lobby, 1800)
            return "lobby now exists and key set"

    if request.method == "GET":
        if not r.exists(lobby):
            d = fixedTemplate()
            for key in d.keys():
                r.hset(lobby, key, d[key])
        data = {}
        data['server'] = r.hget(lobby, "server")
        data['mapIdx'] = r.hget(lobby, "mapIdx")
        circleIds = []
        for i in range(128):
            circleIds.append(r.hget(lobby, i))
        data['markerPiIdxs'] = circleIds
        print("hmmm", data)
        r.expire(lobby, 1800)
        return json.dumps(data)
    
    return "UNSUPPORTED"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
