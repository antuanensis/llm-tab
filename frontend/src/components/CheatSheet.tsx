interface Props {
  text: string;
}

export function CheatSheet({ text }: Props) {
  return (
    <section className="section cheat-sheet">
      <h3>Cheat Sheet</h3>
      <p className="cheat-text">{text}</p>
    </section>
  );
}
