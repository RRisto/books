## Per year

```dataviewjs
const pages = dv.pages('"Books/Library"')
  .where(p => p.year_finished > 0)
  .groupBy(p => p.year_finished)
  .sort(g => g.key);

const years = pages.map(g => g.key);
const counts = pages.map(g => g.rows.length);

const chartData = `\`\`\`chart
type: line
labels: [${years.join(', ')}]
series:
  - title: Books
    data: [${counts.join(', ')}]
\`\`\``;

dv.paragraph(chartData);
```

```dataviewjs
const pages = dv.pages('"Books/Library"')
  .where(p => p.year_finished > 0)
  .groupBy(p => p.year_finished)
  .sort(g => g.key);

const years = pages.map(g => g.key);
const pageCounts = pages.map(g => g.rows.pages.sum());

const chartData = `\`\`\`chart
type: line
labels: [${years.join(', ')}]
series:
  - title: Pages
    data: [${pageCounts.join(', ')}]
\`\`\``;

dv.paragraph(chartData);
```


```dataview
TABLE WITHOUT ID year_finished AS "Year", length(rows) AS "Books", sum(rows.pages) AS "Pages"
FROM "Books/Library"
WHERE year_finished > 0 AND pages > 0
GROUP BY year_finished
SORT year_finished DESC
```



## Per month

```dataviewjs
const pages = dv.pages('"Books/Library"')
  .where(p => p.month_finished)
  .groupBy(p => p.month_finished.toString().substring(0, 7))
  .sort(g => g.key);

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const labels = pages.map(g => {
  const [year, month] = g.key.split('-');
  return `${monthNames[parseInt(month) - 1]} ${year}`;
});
const bookCounts = pages.map(g => g.rows.length);

const chartData = `\`\`\`chart
type: line
labels: [${labels.map(l => `"${l}"`).join(', ')}]
series:
  - title: Books
    data: [${bookCounts.join(', ')}]
\`\`\``;

dv.paragraph(chartData);
```


```dataviewjs
const pages = dv.pages('"Books/Library"')
  .where(p => p.month_finished)
  .groupBy(p => p.month_finished.toString().substring(0, 7))
  .sort(g => g.key);

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const labels = pages.map(g => {
  const [year, month] = g.key.split('-');
  return `${monthNames[parseInt(month) - 1]} ${year}`;
});
const pageCounts = pages.map(g => g.rows.pages.sum());

const chartData = `\`\`\`chart
type: line
labels: [${labels.map(l => `"${l}"`).join(', ')}]
series:
  - title: Pages
    data: [${pageCounts.join(', ')}]
\`\`\``;

dv.paragraph(chartData);
```





```dataview
TABLE WITHOUT ID month_finished AS "Month", length(rows) AS "Books", sum(rows.pages) AS "Pages"
FROM "Books/Library"
WHERE month_finished != ""
GROUP BY month_finished
SORT month_finished DESC
```

