# 🍳 Mange-ta-Main: Recipe Analytics Dashboard

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.50-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A comprehensive data analytics platform for exploring food recipes, nutritional patterns, and user interactions from the Food.com dataset**

## ✨ Features

### 🔍 **Data Exploration**
- **Recipe Database**: Explore thousands of recipes with detailed nutritional information
- **User Interactions**: Analyze ratings, reviews, and cooking patterns
- **Interactive Visualizations**: Dynamic charts and plots powered by Plotly

### 📊 **Analytics Pages**
- **🏠 Data Overview**: Basic dataset exploration and statistics  
- **🍎 Healthiness Analysis**: Nutritional score analysis and healthy recipe identification
- **🏆 Popular Recipes**: Trending recipes and popularity metrics analysis
- **👨‍🍳 Contributor Activity**: User engagement and contribution patterns
- **🍽️ To Cook or Not to Cook**: Cooking complexity and decision analysis
- **🏷️ Tag Analysis**: Recipe categorization and tag co-occurrence patterns
- **📈 NutriCorrelation**: Nutritional component relationships and correlations

### 🎯 **Key Capabilities**
- **Machine Learning**: K-means clustering, PCA analysis, and predictive modeling
- **Statistical Analysis**: Correlation analysis, distribution studies, and trend identification
- **Data Visualization**: Interactive plots, heatmaps, and statistical charts
- **Real-time Processing**: Fast data loading and responsive user interface

## 🚀 Quick Start

### Prerequisites
- Python 3.12
- 2GB+ free disk space (for dataset)
- Internet connection (for initial data download)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/mange-ta-main.git
   cd mange-ta-main
   ```

2. **Set up the environment**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Download the dataset**
   ```bash
   # Initialize data (downloads from Kaggle)
   uv run init_data
   ```

4. **Launch the application**
   ```bash
   # Development mode
   uv run app
   
   # Production mode  
   uv run --env production app
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501` to explore the dashboard

## 📁 Project Structure

```
mange-ta-main/
├── src/mange_ta_main/          # Main application code
│   ├── main.py                 # Streamlit entry point
│   ├── pages/                  # Analysis pages
│   │   ├── Healthiness.py      # Nutritional analysis
│   │   ├── Popular_Recipes_Analysis.py
│   │   ├── Contributor_Activity_Analysis.py
│   │   ├── To_cook_or_Not_to_cook.py
│   │   ├── Univariate_Tags.py
│   │   └── Introduction_NutriCorrelation.py
│   ├── utils/                  # Utility functions
│   └── assets/                 # Static assets
├── Data/                       # Dataset storage
│   ├── raw/                    # Data processing scripts
│   └── *.csv, *.pkl           # Processed datasets
├── scripts/                    # Deployment scripts
└── tests/                      # Test suite
```

## 🎮 Usage

### Navigation
The application features a custom navigation bar with the following sections:
- **Data**: Dataset overview and basic statistics
- **Healthiness**: Nutritional analysis and healthy recipe identification  
- **Popular Recipes**: Recipe popularity and trending analysis
- **Contributor Activity**: User engagement metrics
- **Cooking Complexity**: Decision support for recipe selection
- **Tag Analysis**: Recipe categorization insights
- **NutriCorrelation**: Nutritional component relationships

### Data Analysis Features
- **Interactive Filtering**: Filter recipes by nutrition, tags, and complexity
- **Statistical Modeling**: Built-in ML models for pattern recognition
- **Export Capabilities**: Download processed data and visualizations
- **Real-time Updates**: Dynamic charts that update based on selections

## 🔧 Development

### Setup Development Environment
```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest

# Code formatting
black src/
```

### Adding New Pages
1. Create a new Python file in `src/mange_ta_main/pages/`
2. Follow the existing page structure with Streamlit components
3. Import required utilities from `utils/` directory
4. Update navigation in `main.py` if needed

## 📊 Dataset

This project uses the **Food.com Recipes and User Interactions Dataset** from Kaggle:
- **180K+ recipes** with detailed nutritional information
- **700K+ user interactions** including ratings and reviews
- **Recipe metadata**: cooking time, difficulty, ingredients, instructions
- **Nutritional data**: calories, fat, sugar, sodium, protein, saturated fat, carbohydrates

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Pandas, NumPy, Scikit-learn
- **Frontend**: Streamlit, Plotly, Seaborn
- **Data Processing**: NLTK for text analysis
- **ML/Analytics**: K-means clustering, PCA, statistical modeling
- **Package Management**: UV, Hatch
- **Deployment**: Docker-ready with nginx configuration

## 👥 Authors

- **Zaher Hamadeh** - *hamadehzaher0@gmail.com*
- **François-Xavier Bonnefont** - *bonnefontfx@gmail.com*  
- **Oscar De La Cruz** - *odelacruz.fierro@gmail.com*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📈 Performance Notes

- **Initial Setup**: First run requires ~2GB dataset download
- **Memory Usage**: Recommend 8GB+ RAM for full dataset analysis
- **Startup Time**: ~30-60 seconds for complete data loading
- **Browser**: Chrome/Firefox recommended for optimal visualization performance

## 🐛 Troubleshooting

### Common Issues
- **Data not loading**: Run `uv run init_data` to download dataset
- **Memory errors**: Reduce dataset size or increase available RAM
- **Port conflicts**: Change port in production scripts if 8501 is occupied
- **Visualization issues**: Clear browser cache and refresh

### Support
For issues and feature requests, please use the project's issue tracker.

---

*Built with ❤️ for food data enthusiasts and analytics professionals*