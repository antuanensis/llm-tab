import type { PracticeExercise } from "../types/analysis";

interface Props {
  exercises: PracticeExercise[];
}

export function PracticeExercises({ exercises }: Props) {
  if (!exercises.length) return null;
  return (
    <section className="section">
      <h3>Practice Exercises</h3>
      <ol className="exercise-list">
        {exercises.map((ex) => (
          <li key={ex.number}>{ex.description}</li>
        ))}
      </ol>
    </section>
  );
}
