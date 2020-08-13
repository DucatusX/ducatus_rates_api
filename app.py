from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/rates/')
def get_rates():
    fsym = request.args.get('fsym')
    tsyms = request.args.get('tsyms').split(',')

    response = {tsym: convert(fsym, tsym) for tsym in tsyms}

    return jsonify(response)


def convert(fsym, tsym):
    duc_usd_price = 0.06
    ducx_usd_price = 0.6

    if fsym == 'USD' and tsym == 'DUC':
        amount = 1 / duc_usd_price
    elif fsym == 'USD' and tsym == 'DUCX':
        amount = 1 / ducx_usd_price
    elif fsym == 'DUC' and tsym == 'USD':
        amount = duc_usd_price
    elif fsym == 'DUCX' and tsym == 'USD':
        amount = ducx_usd_price
    else:
        amount = 1

    return amount
