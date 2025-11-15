# Student Analytics Presentation

A professional, interactive presentation built with React and Reveal.js showcasing student collaboration and engagement data.

## Features

- 📊 **Interactive Charts** - Beautiful visualizations using Recharts
- 🎨 **Modern Design** - Gradient backgrounds and smooth animations
- 📱 **Responsive** - Works on all screen sizes
- ⌨️ **Keyboard Navigation** - Use arrow keys to navigate slides
- 🎯 **Data-Driven** - Automatically analyzes CSV data

## How to Use

### Starting the Presentation

```bash
npm start
```

The presentation will open at `http://localhost:3000`

### Navigation

- **Arrow Keys** (←/→) - Navigate between slides
- **Space** - Next slide
- **Esc** - Overview mode (see all slides)
- **F** - Fullscreen mode

### Slides Overview

1. **Title Slide** - Introduction
2. **Overview** - Key statistics (total students, avg collaborations, avg interactions)
3. **Communities** - Bar chart showing student distribution across communities
4. **Top Skills** - Horizontal bar chart of most common skills
5. **Skills Distribution** - Pie chart showing skill percentages
6. **Student Interests** - Bar chart of student interests
7. **Key Insights** - Summary cards with important metrics
8. **Conclusion** - Final thoughts and thank you

## Customization

### Changing Data

Replace `/public/dataset_etudiants.csv` with your own CSV file. The presentation will automatically analyze and visualize the new data.

### Modifying Styles

- Edit `src/App.css` for presentation-specific styles
- Modify gradient backgrounds in `src/App.js` using `data-background-gradient` attribute
- Change chart colors in the `COLORS` array

### Adding Slides

Add new `<section>` elements in `src/App.js`:

```jsx
<section data-background-gradient="linear-gradient(135deg, #color1 0%, #color2 100%)">
  <h2>Your Title</h2>
  <div>Your content</div>
</section>
```

## Technologies Used

- **React** - UI framework
- **Reveal.js** - Presentation framework
- **Recharts** - Chart library
- **PapaParse** - CSV parsing (via fetch)

## Tips for Presenting

1. Press **F** for fullscreen before presenting
2. Use **Esc** to see slide overview
3. Practice navigation with arrow keys
4. Charts are interactive - hover to see details
5. All data is loaded from the CSV file automatically

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

---

**Created with ❤️ using React + Reveal.js**
