% ---------------------------------------------------------------------
% Clase para artículos de la revista Ciencias Matemáticas
% Class for Ciencias Matemáticas Journal articles
% Modificada por Damian Valdes Santiago
% ---------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{rcmart}[31/03/2024, v4.0]
\RequirePackage[T1]{fontenc}
\RequirePackage{ifthen}
\RequirePackage{calc}
\AtEndOfClass{\RequirePackage{microtype}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions*
\LoadClass{article}
\RequirePackage{ifpdf}      % Needed to pick between latex and pdflatex
\RequirePackage{widetext}

%----------------------------------------------------------------------
%	FONTS
%----------------------------------------------------------------------

\RequirePackage{times}      % Loads the Times-Roman Fonts
\RequirePackage{mathptmx}   % Loads the Times-Roman Math Fonts

%----------------------------------------------------------------------
%	VARIOUS USEFUL PACKAGES
%----------------------------------------------------------------------

\RequirePackage[utf8]{inputenc}
\RequirePackage{amsmath,amsfonts,amssymb}
\RequirePackage{graphicx,xcolor}
\RequirePackage[english,spanish,es-tabla]{babel}
\RequirePackage[spanish]{babelbib}
\RequirePackage{booktabs}
\RequirePackage{lastpage}

%----------------------------------------------------------------------
%	MARGINS	
%----------------------------------------------------------------------
	  	  
\RequirePackage[left=2cm,%
                right=2cm,%
	            top=2.25cm,%
				bottom=2.25cm,%
				headheight=11pt,%
				letterpaper]{geometry}%
				
%----------------------------------------------------------------------
%	FIGURES AND TABLES CAPTIONS
%----------------------------------------------------------------------

\RequirePackage[labelfont={bf,sf,small},%
                labelsep=period,%
                justification=raggedright]{caption}
\setlength{\abovecaptionskip}{0pt}
\setlength{\belowcaptionskip}{0pt}
				
%----------------------------------------------------------------------
%	PAGE HEADER
%----------------------------------------------------------------------

\RequirePackage{fancyhdr}  % Needed to define custom headers/footers
\RequirePackage{lastpage}  % Number of pages in the document
\pagestyle{fancy}          % Enables the custom headers/footers
% Headers
%\lhead{}%
%\chead{}%
%\rhead{\small\sffamily\bfseries\@PaperTitle\  --- \thepage}
\fancyhead{}
\fancyhead[RO,LE]{\thepage}
\fancyhead[LO,RE]{\small\sffamily\bfseries\@PaperTitle}
% Footers
\fancyfoot{}
\fancyfoot[LE,RO]{\scriptsize\sffamily\bfseries\@JournalInfo\\\@PaperUrl}%
\fancyfoot[RE,LO]{\scriptsize\sffamily\bfseries\@AuthorsAbbrev}%
%\lfoot{\tiny\sffamily\bfseries\@JournalInfo}%
%\cfoot{}%
%\rfoot{\tiny\sffamily\bfseries\@PaperUrl}%
\renewcommand{\headrulewidth}{1pt}% % No header rule
\renewcommand{\footrulewidth}{0pt}% % No footer rule


%----------------------------------------------------------------------
%	SECTION/SUBSECTION/PARAGRAPH SET-UP
%----------------------------------------------------------------------

\RequirePackage[explicit]{titlesec}
\titleformat{\section}
  {\color{color1}\large\sffamily\bfseries}
  {}
  {0em}
  {\colorbox{color2!10}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\centering\arabic{section}. #1}}}
  []
\titleformat{name=\section,numberless}
  {\color{color1}\large\sffamily\bfseries}
  {}
  {0em}
  {\colorbox{color2!10}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\centering#1}}}
  []  
\titleformat{\subsection}
  {\color{color1}\sffamily\bfseries}
  {\thesubsection}
  {0.5em}
  {#1}
  []
\titleformat{\subsubsection}
  {\sffamily\small\bfseries}
  {\thesubsubsection}
  {0.5em}
  {#1}
  []    
\titleformat{\paragraph}[runin]
  {\sffamily\small\bfseries}
  {}
  {0em}
  {#1} 
\titlespacing*{\section}{0pc}{3ex \@plus4pt \@minus3pt}{5pt}
\titlespacing*{\subsection}{0pc}{2.5ex \@plus3pt \@minus2pt}{0pt}
\titlespacing*{\subsubsection}{0pc}{2ex \@plus2.5pt \@minus1.5pt}{0pt}
\titlespacing*{\paragraph}{0pc}{1.5ex \@plus2pt \@minus1pt}{10pt}

%----------------------------------------------------------------------
%	TABLEOFCONTENTS SET-UP
%----------------------------------------------------------------------
\newlength{\tocsep} 
\setlength\tocsep{1.5pc} % Sets the indentation of the sections in the table of contents
\setcounter{tocdepth}{3} % Three levels in the table of contents section: sections, subsections and subsubsections

\usepackage{titletoc}
\contentsmargin{0cm}
\titlecontents{section}[\tocsep]
  {\addvspace{4pt}\small\bfseries\sffamily}
  {\contentslabel[\thecontentslabel]{\tocsep}}
  {}
  {\hfill\thecontentspage}
  []
\titlecontents{subsection}[\tocsep]
  {\addvspace{2pt}\sffamily}
  {\contentslabel[\thecontentslabel]{\tocsep}}
  {}
  {\ \titlerule*[.5pc]{.}\ \thecontentspage}
  []
\titlecontents*{subsubsection}[\tocsep]
  {\footnotesize\sffamily}
  {}
  {}
  {}
  [\ \textbullet\ ]  

%----------------------------------------------------------------------
%	MULTIPLE AUTHOR SET
%----------------------------------------------------------------------  
  
\newcount\@authcnt
\newcount\@tmpcnt\@tmpcnt\z@

\def\@affiliation{%
  \ifnum\@tmpcnt<\@authcnt
   \global\advance\@tmpcnt1
    \raggedright \csname @auth\romannumeral\the\@tmpcnt\endcsname\hfill\\%
   \let\next\@affiliation \vskip1pt
  \else
   \let\next\relax
  \fi
\next}
	 
\newcommand{\affiliation}[1]{%
    \global\advance\@authcnt1
    \expandafter\gdef\csname @auth\romannumeral\the\@authcnt\endcsname
    {#1}}

	
%----------------------------------------------------------------------
%	LIST CONTROL
%----------------------------------------------------------------------  

\RequirePackage{enumitem}
%\setlist{nolistsep} % Uncomment to remove spacing between items in lists (enumerate, itemize)

%----------------------------------------------------------------------
%	ABSTRACT+AUTHOR FRAME
%----------------------------------------------------------------------  

\newcommand{\PaperTitle}[1]{\def\@PaperTitle{#1}}
\newcommand{\PaperTitleEng}[1]{\def\@PaperTitleEng{#1}}
\newcommand{\Archive}[1]{\def\@Archive{#1}}
\newcommand{\Authors}[1]{\def\@Authors{#1}}
\newcommand{\AuthorsAbbrev}[1]{\def\@AuthorsAbbrev{#1}}
\newcommand{\JournalInfo}[1]{\def\@JournalInfo{#1}}
\newcommand{\PaperUrl}[1]{\def\@PaperUrl{#1}}
\newcommand{\Resumen}[1]{\def\@Resumen{#1}}
\newcommand{\Abstract}[1]{\def\@Abstract{#1}}
\newcommand{\Pclaves}[1]{\def\@Pclaves{#1}}
\newcommand{\Keywords}[1]{\def\@Keywords{#1}}
\newcommand{\MSC}[1]{\def\@MSC{#1}}
\newcommand{\Autocita}[1]{\def\@Autocita{#1}}
\newcommand{\SectionInfo}[1]{\def\@SectionInfo{#1}}

% ---------------------------------------------------------------------

\renewcommand{\@maketitle}{%
\twocolumn[{%
	\thispagestyle{empty}%
	\vskip-36pt%
	{\raggedright\fbox{\normalsize\sffamily\bfseries\@SectionInfo\par}}%
	\vskip20pt%
	\vskip-36pt%
	{\raggedleft\small\sffamily\bfseries\@JournalInfo\\\@Archive\par}%
	\vskip20pt%
	{\raggedright\color{color1}\sffamily\bfseries\fontsize{20}{25}\selectfont \@PaperTitle\par \textit{\@PaperTitleEng}\par}%
	\vskip10pt%
	{\raggedright\color{color1}\sffamily\fontsize{12}{16}\selectfont  \@Authors\par}%
	\vskip18pt%
	\fcolorbox{color1}{white}{%
		\parbox{\textwidth-2\fboxsep-2\fboxrule}{\centering%
			\colorbox{color2!10}{%
				\parbox{\textwidth-4\fboxsep-2\fboxrule}{%
					\ifx\@Keywords\@empty%
						\selectlanguage{spanish}
						\sffamily\textbf{\abstractname}\quad\@Resumen\par\smallskip%
						\selectlanguage{english}
						\sffamily\textbf{\abstractname}\quad\@Abstract\par%
					\else%
						\selectlanguage{spanish}
						\sffamily\textbf{\abstractname}\quad\@Resumen\par\smallskip%
						\textbf{Palabras Clave:} \@Pclaves\par\smallskip%
						\selectlanguage{english}
						\textit{\sffamily\textbf{\abstractname}\quad\@Abstract}\par\smallskip%
						\textbf{\textit{Keywords:}} \textit{\@Keywords}\par\smallskip%
						\textbf{Mathematics Subject Classification:} \@MSC
					\fi%
				}%
			}%
		\vskip4pt%
		\begingroup%
		\raggedright\sffamily\small%
		\footnotesize\@affiliation\par%
		\endgroup%%
		}%
	}%
	\vskip5pt%
	\fcolorbox{white}{white}{%
		\parbox{\textwidth-2\fboxsep-2\fboxrule}{\centering%
			\colorbox{color2!3}{%
				\parbox{\textwidth-4\fboxsep-2\fboxrule}{%
						\sffamily\textbf{Citar como:}\quad\@Autocita\par\smallskip%
				}%
			}%
		}%
	}%
	\vskip25pt%
}]%
}%