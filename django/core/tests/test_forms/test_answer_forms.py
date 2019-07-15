from config.universal_tests import UniversalFormTest
from core.forms import AnswerForm
from core.models import Answer

class TestAnswerForm(UniversalFormTest):
    form_class = AnswerForm
    form_model_class = Answer
