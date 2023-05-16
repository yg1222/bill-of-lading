from flask import Flask, flash, render_template, redirect, request, \
     session, make_response, send_file, url_for, flash, send_from_directory, \
        current_app, Blueprint, render_template, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, \
    current_user, logout_user
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from xhtml2pdf import pisa
from datetime import datetime
from bleach import clean

import logging
import io
import os

from itertools import zip_longest
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid as uuid

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, \
    SelectField
from wtforms.validators import DataRequired, Regexp, Email, Length

from werkzeug.utils import secure_filename

from jinja2 import Environment



