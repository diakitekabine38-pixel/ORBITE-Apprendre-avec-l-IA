"""Server-side grading. Questions' correct answers never reach the client."""

from .models import Attempt, Question

XP_QUIZ = 50


def is_correct(question, answer):
    qtype = question.question_type
    correct = question.correct or []

    if qtype in (Question.TYPE_MCQ, Question.TYPE_TRUE_FALSE):
        return answer == correct[0] if correct else False
    if qtype == Question.TYPE_MULTIPLE:
        return set(answer or []) == set(correct)
    if qtype == Question.TYPE_ORDERING:
        return list(answer or []) == list(correct)
    if qtype == Question.TYPE_OPEN:
        # Lightweight keyword overlap heuristic; the LLM evaluator can refine it.
        if not answer or not correct:
            return bool(answer)
        text = str(answer).lower()
        hits = sum(1 for kw in correct if str(kw).lower() in text)
        return hits / len(correct) >= 0.5 if correct else bool(text)
    if qtype == Question.TYPE_ASSOCIATION:
        return dict(answer or {}) == dict(correct)
    return False


def grade_attempt(user, quiz, answers, time_spent_seconds=0):
    """Compute the final score for an attempt and award XP on success."""
    questions = list(quiz.questions.all())
    total_points = sum(q.points for q in questions)
    earned = 0
    detail = []
    answers_by_qid = {a.get("question_id"): a.get("answer") for a in answers}

    for question in questions:
        answer = answers_by_qid.get(question.id)
        ok = is_correct(question, answer)
        earned += question.points if ok else 0
        detail.append({"question_id": question.id, "correct": ok})

    score = round(earned / total_points * 100, 1) if total_points else 0.0
    passed = score >= quiz.pass_score

    attempt = Attempt.objects.create(
        quiz=quiz,
        user=user,
        answers=answers,
        score=score,
        passed=passed,
        time_spent_seconds=time_spent_seconds,
    )
    if passed:
        user.add_xp(XP_QUIZ)
        # Push a mastery signal into the skills layer when the quiz links a skill.
        for q in questions:
            _touch_skill(user, quiz)
    return attempt, detail


def _touch_skill(user, quiz):
    from apps.learning.models import Skill, UserSkill

    course = quiz.lesson.module.course
    skill, _ = Skill.objects.get_or_create(
        name=f"{course.title} (quiz)", slug=f"quiz-{course.slug}"
    )
    usk, _ = UserSkill.objects.get_or_create(user=user, skill=skill)
    usk.mastery_score = min(100, usk.mastery_score + 5)
    usk.save()