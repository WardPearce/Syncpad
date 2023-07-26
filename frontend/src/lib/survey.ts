import { normalizeSurveyQuestions } from "../components/Survey/helpers";
import type { rawChoice, rawQuestion } from "../components/Survey/types";
import type { SurveyModel, SurveyPublicModel, SurveyQuestionModel, SurveyResultModel } from "./client";
import publicKey from "./crypto/publicKey";
import secretKey from "./crypto/secretKey";
import signatures from "./crypto/signatures";


export interface RawQuestionAnswer extends rawQuestion {
  answer: number | number[] | string | null;
  error: string | null;
}

export interface RawAnswer {
  id: number;
  type: SurveyQuestionModel.type;
  answer: string | string[];
}

export interface RawSurvey {
  title: string;
  description: string | undefined;
  questions: RawQuestionAnswer[];
}


export function* decryptAnswers(
  rawPublicKey: Uint8Array,
  rawPrivateKey: Uint8Array,
  result: SurveyResultModel
): Generator<RawAnswer> {

  for (const answer of result.answers) {
    if (answer.answer instanceof Array) {
      const multipleChoiceAnswers: string[] = [];
      answer.answer.forEach((choice) => {
        multipleChoiceAnswers.push(
          publicKey.boxSealOpen(
            rawPublicKey,
            rawPrivateKey,
            choice,
            true
          ) as string
        );
      });

      yield {
        id: answer.id,
        type: answer.type,
        answer: multipleChoiceAnswers,
      };
    } else {
      yield {
        id: answer.id,
        type: answer.type,
        answer: publicKey.boxSealOpen(
          rawPublicKey,
          rawPrivateKey,
          answer.answer,
          true
        ) as string,
      };
    }
  }

}


export function validateSurvey(rawSignPublicKey: Uint8Array, survey: SurveyModel | SurveyPublicModel) {
  const toValidate: Record<string, any> = {
    title: {
      cipher_text: survey.title.cipher_text,
      iv: survey.title.iv,
    },
    questions: normalizeSurveyQuestions(survey.questions),
    keypair: {
      public_key: {
        cipher_text: survey.keypair.public_key.cipher_text,
        iv: survey.keypair.public_key.iv,
      },
    },
  };

  if (survey.description) {
    toValidate.description = {
      cipher_text: survey.description.cipher_text,
      iv: survey.description.iv,
    };
  }

  signatures.validateHash(
    rawSignPublicKey,
    survey.signature,
    JSON.stringify(toValidate)
  );

}

export function decryptSurveyQuestions(rawKey: Uint8Array, survey: SurveyModel | SurveyPublicModel): RawSurvey {
  const rawQuestions: RawQuestionAnswer[] = [];

  const rawTitle = secretKey.decrypt(
    rawKey,
    survey.title.iv,
    survey.title.cipher_text,
    true
  ) as string;

  let rawDescription: undefined | string;
  if (survey.description)
    rawDescription = secretKey.decrypt(
      rawKey,
      survey.description.iv,
      survey.description.cipher_text,
      true
    ) as string;

  survey.questions.forEach((question) => {
    let choices: rawChoice[] = [];
    if (question.choices)
      question.choices.forEach((choice) => {
        choices.push({
          id: choice.id,
          choice: secretKey.decrypt(
            rawKey,
            choice.iv,
            choice.cipher_text,
            true
          ) as string,
        });
      });

    let rawRegex: string | null = null;
    if (question.regex) {
      rawRegex = secretKey.decrypt(
        rawKey,
        question.regex.iv,
        question.regex.cipher_text,
        true
      ) as string;
    }

    rawQuestions.push({
      id: question.id,
      question: secretKey.decrypt(
        rawKey,
        question.question.iv,
        question.question.cipher_text,
        true
      ) as string,
      description: question.description
        ? (secretKey.decrypt(
          rawKey,
          question.description.iv,
          question.description.cipher_text,
          true
        ) as string)
        : null,
      required: question.required as boolean,
      type: question.type,
      choices: choices,
      regex: rawRegex,
      answer: null,
      error: null,
    });
  });

  return {
    title: rawTitle,
    description: rawDescription,
    questions: rawQuestions,
  };
}