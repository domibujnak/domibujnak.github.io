const ORCID = "0000-0001-8043-9897";

function formatAuthors(authors: string[]) {

  return authors.map((author) => {

    author = author.trim();

    if (author.includes("du Plessis")) {
      return "du Plessis S.J.";
    }

    // already citation style:
   if (author.match(/,\s*[A-Z]/)) {

  const parts = author
    .replace(",", "")
    .trim()
    .split(/\s+/);

  const formatted = `${parts[0]} ${parts.slice(1).join("")}`;

  if (parts[0].includes("Bujnáková")) {
    return `<strong>${formatted}</strong>`;
  }

  return formatted;
}

    const parts = author.split(/\s+/);

    if (parts.length < 2) {
      return author;
    }

    const surname = parts[parts.length - 1];
    const given = parts.slice(0,-1);

    const initials = given
      .map((n) => n.replace(".","")[0])
      .join(".");

const formatted = `${surname} ${initials}.`;

if (surname.includes("Bujnáková")) {
  return `<strong>${formatted}</strong>`;
}

return formatted;

  }).join(", ");

}

export async function getPublications() {
  const response = await fetch(
    `https://pub.orcid.org/v3.0/${ORCID}/works`,
    {
      headers: {
        Accept: "application/json",
      },
    }
  );


  const data = await response.json();

  const publications = await Promise.all(
    data.group.map(async (work: any) => {
      const summary = work["work-summary"][0];

      const putCode = summary["put-code"];

      const detailResponse = await fetch(
        `https://pub.orcid.org/v3.0/${ORCID}/work/${putCode}`,
        {
          headers: {
            Accept: "application/json",
          },
        }
      );

      const detail = await detailResponse.json();

      const contributors =
  detail.contributors?.contributor
    ?.map((person: any) => {

      const name = person["credit-name"]?.value;

      if (!name) return null;

      return name;

    })
    .filter(Boolean) ?? "";

      return {
  year: summary["publication-date"]?.year?.value ?? "",
  title: summary.title.title.value,
  journal: summary["journal-title"]?.value ?? "",
  doi:
    summary["external-ids"]?.["external-id"]?.find(
      (id: any) => id["external-id-type"] === "doi"
    )?.["external-id-value"] ?? "",
authors: formatAuthors(contributors),};
    })
  );

  return publications;
}