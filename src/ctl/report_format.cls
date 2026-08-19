
\ProvidesClass{report_format}[2026/07/16 Example Project Report Class]
\LoadClass[]{article}

\RequirePackage{geometry}
\RequirePackage{xcolor}
\RequirePackage{tikz}
\RequirePackage{tcolorbox}
\RequirePackage{fancyhdr}
\RequirePackage{amssymb}
\RequirePackage[hidelinks]{hyperref}
\RequirePackage{tabularx, booktabs}
\RequirePackage{lmodern}
\RequirePackage{array}
\RequirePackage{colortbl}



\definecolor{purp}{HTML}{310062}
\definecolor{lightgrey}{HTML}{F5F5F5}
\definecolor{darkgrey}{HTML}{333333}
\definecolor{insertion}{HTML}{2EA043}
\definecolor{deletion}{HTML}{D73A49}
\definecolor{verified}{HTML}{0066FF}


\color{darkgrey}


\newcommand{\drawcorners}{%
  \begin{tikzpicture}[remember picture, overlay]
    \fill[purp] ([xshift=-4.5cm]current page.north east) -- 
                ([xshift=-3.9cm, yshift=-0.6cm]current page.north east) -- 
                ([xshift=-0.6cm, yshift=-0.6cm]current page.north east) -- 
                ([xshift=-0.6cm, yshift=-3.9cm]current page.north east) -- 
                ([yshift=-4.5cm]current page.north east) -- 
                (current page.north east) -- cycle;

    \fill[purp] ([yshift=4.5cm]current page.south west) -- 
                ([yshift=3.9cm, xshift=0.6cm]current page.south west) -- 
                ([xshift=0.6cm, yshift=0.6cm]current page.south west) -- 
                ([xshift=3.9cm, yshift=0.6cm]current page.south west) -- 
                ([xshift=4.5cm]current page.south west) -- 
                (current page.south west) -- cycle;
  \end{tikzpicture}%
}


\AddToHook{shipout/background}{\drawcorners}

\renewcommand{\familydefault}{\sfdefault}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\thepage}

\renewcommand{\arraystretch}{1.3}

