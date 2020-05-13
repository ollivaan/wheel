# -*- coding: utf-8 -*-
from flask import render_template


import codecs
from random import shuffle

from flask import Blueprint, current_app, Flask, render_template

from .evaluation import Evaluator
from .loader import load
from .userinput import UserInput

import json
import plotly

import pandas as pd
import numpy as np
import plotly.express as px
import os
from pathlib import Path



# Import Dash application
from application.plotlydash.dashboard import create_dashboard
from application.assets import compile_assets

blueprint = Blueprint('blueprint', __name__)


def create_app(filename):
    if not filename:
        raise Exception('No configuration filename specified.')

    with codecs.open(filename, encoding='utf-8') as f:
        questionnaire, rating_levels = load(f)

    evaluator = Evaluator(rating_levels)

    return _create_app(questionnaire, evaluator)


def _create_app(questionnaire, evaluator):
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
#    app.config.from_object('config.Config')

    app.register_blueprint(blueprint)

    app.questionnaire = questionnaire
    app.evaluator = evaluator

    with app.app_context():

        
        app = create_dashboard(app)
        # Compile CSS
        compile_assets(app)

        return app



@blueprint.app_template_filter()
def shuffled(iterable):
    """Return a shuffled copy of the given iterable."""
    l = list(iterable)
    shuffle(l)
    return l


@blueprint.app_context_processor
def inject_title():
    return {
        'title': current_app.questionnaire.title,
    }


@blueprint.route('/', methods=['GET'])
def view():
    output = {
        'questionnaire': current_app.questionnaire,
    }
    answers = Path("./data/user_answers.csv")
    if answers.is_file():
        os.remove(answers)

    return render_template('questionnaire.html', **output)

@blueprint.route('/', methods=['GET'])
def dash():
    """Landing page."""
    return render_template('')


@blueprint.route('/', methods=['POST'])
def evaluate():
    user_input = UserInput.from_request(current_app.questionnaire)

    output = {
        'username': user_input.name,
    }

    if user_input.all_questions_answered:
        result = current_app.evaluator.get_result(current_app.questionnaire,
                                                  user_input)
        output['result'] = result
        return render_template('result.html', **output)
    else:
        output['questionnaire'] = current_app.questionnaire
        output['user_input'] = user_input
        return render_template('questionnaire.html', **output)


