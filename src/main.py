from bf import BFEvaluator

import xml.sax.saxutils as saxutils

from flask import Flask
from flask import request
from flask import jsonify
from flask import current_app

import requests

def get_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    return app

app = get_app()

'''
    Utils
'''

def execute_bf_code(code):
    evaluator = BFEvaluator()

    try:
        success, output = evaluator.evaluate(code)
    except Exception:
        return (False, '')
    else:
        return (success, output)

'''
    Response Utils
'''

def notify_webhook(hook, text):
    try:
        requests.post(hook, json={'text': text})
    except Exception:
        print('SLACK_MESSAGE_HOOK not configured, skipping message send')

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
        source = saxutils.unescape(request.form['text'])
        trigger = request.form['trigger_word']
        source = source[len(trigger):]
    except KeyError as ke:
        return make_slack_response('Missing source in request.')
    except Exception as e:
        return make_slack_response('Unexpected error while processing request.')
    else:
        success, output = execute_bf_code(source)

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
        success, output = execute_bf_code(source)

        if success:
            notify_webhook(current_app.config.get('SLACK_MESSAGE_HOOK', ''), 'Entry Success: ```{}``` Source: ```{}```'.format(output, source))
            return make_success('Program successfully submitted!', data={'output': output})
        else:
            return make_error('Program failed to be interpreted. Please check source for errors.')

'''
    Startup
'''

def main():
    app.run(host=app.config.get('HOST', '0.0.0.0'), debug=app.config.get('DEBUG', True))

if __name__ == '__main__':
    main()
