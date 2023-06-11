<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://cvproject.ru">
    <img src="design/logo.svg" alt="Logo" width="180">
  </a>

  <p align="center">
    <br />
    <a href="https://cvproject.ru"><strong>Go to web-site »</strong></a>
    <br />
    <br />
    <a href="https://github.com/kosdmit/cv_project/issues">Report Bug</a>
    ·
    <a href="https://github.com/kosdmit/cv_project/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://cvproject.ru)

This project is a job search web application designed to empower job seekers by providing a platform where they can 
create and publish their resumes. Beyond merely being a job search site, this application integrates social networking 
features to foster a community of users who can interact, share, and support each other throughout their job search
journey. The application also includes a microblogging feature where users can post information about job hunting, 
technologies, and more.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python]][Python-url]
* [![Django][Django]][Django-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![HTML][HTML]][HTML-url]
* [![CSS][CSS]][CSS-url]
* [![JS][JS]][JS-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

If you're interested just in using this, you can start by visiting the website: <a href="https://cvproject.ru">cvproject.ru</a>

Below is instruction on setting up this project locally.
To get a local copy up and running follow these simple steps.

### Prerequisites
_Let's check if we are ready._

* This project uses Python 3.8. Check your python version:
  ```sh
  python --version
  ```

### Installation

_Let`s start._

1. Clone the repo
   ```sh
   git clone https://github.com/kosdmit/CV_project.git
   ```
2. Create and activate a virtual environment
   ```sh
   cd yourrepository
   virtualenv venv
   venv\Scripts\activate
   ```
   If you are on Unix or MacOS, run this for activate virtual environment:  
   ```sh
   source venv\Scripts\activate
   ```

3. Install required Python packages
   ```sh
   pip install -r requirements.txt
   ```
   
4. Create and apply migrations
   ```sh
   python mange.py makemigrations
   python manage.py migrate
   ```
   
5. That`s it! Run the Django server and use how you want!
   ```sh
   python manage.py runserver
   ```

NOTE: You also need to set some variables to system environment or adjust some settings in the settings.py file of the Django project, such as DATABASES, SECRET_KEY, and DEBUG. 
Also, you can create a .env file for sensitive data that shouldn't be exposed in the code.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Additional screenshots

| Discovering page                                               | Blog page                                                    | Comment modal window                                         |
|--------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| [![Screenshot 1][product-screenshot1]](https://cvproject.ru/social/resume_list) | [![Screenshot 2][product-screenshot2]](https://cvproject.ru/social/post_list) | [![Screenshot 3][product-screenshot3]](https://cvproject.ru/resume/kosdmit/) |


_For more examples, simply open [cvproject.ru](https://cvproject.ru) and start use it :)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Release
- [x] Blogs have been added
- [ ] Improve blogs, add articles
- [ ] Add email send lists and subscriptions
- [ ] Multi-language Support
    - [ ] English
    - [ ] Turkey

See the [open issues](https://github.com/kosdmit/cv_project/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Dmitry Kosyrkov - [@kosdmit](https://vk.com/kosdmit) - kosdmit@hotmail.com

Project Link: [https://github.com/kosdmit/cv_project](https://github.com/kosdmit/cv_project)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Font Awesome](https://fontawesome.com)
* [Pillow](https://github.com/python-pillow/Pillow)

And people who help me and give a feedback:
* [Sergey - full-stack web-developer](https://github.com/richsergsam)
* [Vladislav - web-designer](https://vk.com/vladislavzvyagin)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/kosdmit/cv_project.svg?style=for-the-badge
[contributors-url]: https://github.com/kosdmit/cv_project/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/kosdmit/cv_project.svg?style=for-the-badge
[forks-url]: https://github.com/kosdmit/cv_project/network/members
[stars-shield]: https://img.shields.io/github/stars/kosdmit/cv_project.svg?style=for-the-badge
[stars-url]: https://github.com/kosdmit/cv_project/stargazers
[issues-shield]: https://img.shields.io/github/issues/kosdmit/cv_project.svg?style=for-the-badge
[issues-url]: https://github.com/kosdmit/cv_project/issues
[license-shield]: https://img.shields.io/github/license/kosdmit/cv_project.svg?style=for-the-badge
[license-url]: https://github.com/kosdmit/cv_project/blob/master/LICENSE.txt

[product-screenshot]: design/screenshot.png
[product-screenshot1]: design/screenshot1.PNG
[product-screenshot2]: design/screenshot2.PNG
[product-screenshot3]: design/screenshot3.PNG

[Python]: https://img.shields.io/badge/python-%2314354c.svg?logo=python&logoColor=white&style=for-the-badge
[Python-url]: https://www.python.org/
[Django]: https://img.shields.io/badge/django-%23092e20.svg?logo=django&logoColor=white&style=for-the-badge
[Django-url]: https://www.djangoproject.com/
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[HTML]: https://img.shields.io/badge/html5-%23e34f26.svg?logo=html5&logoColor=white&style=for-the-badge
[HTML-url]: https://html.spec.whatwg.org/multipage/
[CSS]: https://img.shields.io/badge/css3-%231572b6.svg?logo=css3&logoColor=white&style=for-the-badge
[CSS-url]: https://www.w3.org/Style/CSS/
[JS]: https://img.shields.io/badge/javascript-%23323330.svg?logo=javascript&logoColor=%23F7DF1E&style=for-the-badge
[JS-url]: https://www.ecma-international.org/publications-and-standards/standards/ecma-262/



