import wtf from 'wtf_wikipedia'
import fs from 'fs'
import path from 'path'

// Funktion zum Generieren der Monatsnamen
function getMonthName(month) {
  return new Date(0, month - 1).toLocaleString('en-US', { month: 'long' })
}

// Funktion zum Speichern der Daten für einen bestimmten Monat
async function fetchAndSave(
  startYear,
  startMonth,
  endYear,
  endMonth,
  outputFolder
) {
  let currentYear = startYear
  let currentMonth = startMonth

  while (
    currentYear < endYear ||
    (currentYear === endYear && currentMonth <= endMonth)
  ) {
    const monthName = getMonthName(currentMonth)
    const pageTitle = `${monthName} ${currentYear}`
    console.log(`Fetching: ${pageTitle}`)

    try {
      let doc = await wtf.fetch(pageTitle)
      if (doc) {
        const outputPath = path.join(
          outputFolder,
          `${currentYear}-${String(currentMonth).padStart(2, '0')}.json`
        )
        fs.writeFileSync(outputPath, JSON.stringify(doc.json(), null, 2))
        console.log(`Saved: ${outputPath}`)
      } else {
        console.log(`No content found for ${pageTitle}`)
      }
    } catch (error) {
      console.error(`Error fetching ${pageTitle}:`, error)
    }

    // Update currentMonth and currentYear for the next iteration
    if (currentMonth === 12) {
      currentMonth = 1
      currentYear += 1
    } else {
      currentMonth += 1
    }
  }
}

fetchAndSave(1924, 2, 1928, 2, 'scraped')
