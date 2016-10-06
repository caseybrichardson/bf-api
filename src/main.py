from bf import BFEvaluator

from flask import Flask
from flask import request
from flask import jsonify

def get_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    return app

app = get_app()

'''
    Utils
'''

def make_slack_response(text):
    response = jsonify({'text': text})
    return response

def make_error(message, data=None, response_code=400):
  return _make_response(message=message, data=data, response_code=response_code)

def make_success(message, data=None, response_code=200):
  return _make_response(message=message, data=data, response_code=response_code)

def _make_response(message, data, response_code):
  response = jsonify({"message": message, "data": data})
  response.status_code = response_code
  return response

'''
    Routes
'''

@app.route('/slack/submit', methods=['POST'])
def slack_submit():
    try:
        source = request.json['text']
        trigger = request.json['trigger_word']
        source = source[len(trigger):]
    except KeyError as ke:
        return make_slack_response('Missing source in request.')
    except Exception as e:
        return make_slack_response('Unexpected error while processing request.')
    else:
        evaluator = BFEvaluator()
        success, output = evaluator.evaluate(source)
        if success:
            return make_slack_response('Program successfully submitted! Output: ```{}```'.format(output.strip()))
        else:
            return make_slack_response('Program failed to be interpreted. Please check source for errors.')

@app.route('/challenge/submit', methods=['POST'])
def challenge_submit():
    try:
        source = request.json['source']
    except KeyError as ke:
        return make_error('Missing source in request.')
    except Exception as e:
        return make_error('Unexpected error while processing request.', response_code=500)
    else:
        evaluator = BFEvaluator()
        success, output = evaluator.evaluate(source)
        if success:
            return make_success('Program successfully submitted!', data={'output': output})
        else:
            return make_error('Program failed to be interpreted. Please check source for errors.')

'''
    Startup
'''

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()