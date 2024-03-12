from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from pydantic import BaseModel

from chatpilot.apps.auth_utils import get_admin_user

router = APIRouter()


class SetDefaultModelsForm(BaseModel):
    models: str


class PromptSuggestion(BaseModel):
    title: List[str]
    content: str


class SetDefaultSuggestionsForm(BaseModel):
    suggestions: List[PromptSuggestion]


############################
# SetDefaultModels
############################


@router.post("/default/models", response_model=str)
async def set_global_default_models(
        request: Request, form_data: SetDefaultModelsForm, user=Depends(get_admin_user)
):
    request.app.state.DEFAULT_MODELS = form_data.models
    return request.app.state.DEFAULT_MODELS


@router.post("/default/suggestions", response_model=List[PromptSuggestion])
async def set_global_default_suggestions(
        request: Request,
        form_data: SetDefaultSuggestionsForm,
        user=Depends(get_admin_user),
):
    data = form_data.dict()
    request.app.state.DEFAULT_PROMPT_SUGGESTIONS = data["suggestions"]
    return request.app.state.DEFAULT_PROMPT_SUGGESTIONS
