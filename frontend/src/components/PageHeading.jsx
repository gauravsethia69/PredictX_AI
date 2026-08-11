export default function PageHeading({ eyebrow = "PredictX AI", title, description, right }) {
  return (
    <div className="dashboard-heading">
      <div>
        <span>{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {right}
    </div>
  );
}
