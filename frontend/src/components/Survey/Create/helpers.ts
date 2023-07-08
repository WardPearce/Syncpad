import type { SurveyChoicesModel, SurveyQuestionModel } from "../../../lib/client";

export function selectOnClick(event: Event) {
  const inputElement = event.target as HTMLInputElement;
  inputElement.select();
}

export function normalizeSurveyQuestions(questions: SurveyQuestionModel[]): SurveyQuestionModel[] {
  let normalizedQuestions: SurveyQuestionModel[] = [];

  questions.sort((a, b) => a.id - b.id).forEach((survey) => {
    const normalizedChoices: SurveyChoicesModel[] = [];

    if (survey.choices)
      survey.choices.sort((a, b) => a.id - b.id).forEach(choice => {
        normalizedChoices.push({
          id: choice.id,
          iv: choice.iv,
          cipher_text: choice.cipher_text
        });
      });

    normalizedQuestions.push({
      id: survey.id,
      regex: survey.regex ? {
        iv: survey.regex.iv,
        cipher_text: survey.regex.cipher_text
      } : null,
      description: survey.description ? {
        iv: survey.description.iv,
        cipher_text: survey.description.cipher_text
      } : null,
      question: survey.question ? {
        iv: survey.question.iv,
        cipher_text: survey.question.cipher_text
      } : null,
      choices: normalizedChoices ? normalizedChoices : null,
      required: survey.required,
      type: survey.type
    });
  });

  return normalizedQuestions;
}
