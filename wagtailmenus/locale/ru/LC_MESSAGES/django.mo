��    D      <  a   \      �     �  "   �  #      #   D  ,   h     �     �     �     �  G   �  �   %  �   
     �     �     	     	     ,	     4	     K	  
   k	     v	     �	  2   
  6   F
  	   }
     �
     �
  {   �
     ?  Q   T  6   �  m   �     K     P     e  c   n  �   �  �   �  *   p  3   �     �  	   �  �   �  @   }  M   �  S        `     }  N   �  	   �  
   �     �     �  	   �            	   6     @  	   O     Y  
   o     z     �     �     �     �     �  "  �  O   �  M   J  K   �  K   �  p   0  E   �  )   �  >        P  �   k  �    �  �     :  #   O     s  %   �     �  +   �  4   �     .  F   F  �   �  }   �  �        �  ,   �  :   �  �     D   �  �   9  �   �  �   e      E!  )   X!     �!  �   �!  D  \"  D  �#  L   �$  Z   3%  A   �%      �%  �   �%  �   �&  �   �'  �   R(  D   )     S)  �   o)     *     4*     L*     _*     {*  .   �*  7   �*     �*  <   +     O+  1   g+     �+     �+  $   �+  .   �+     &,  >   /,     n,               C          (       .   0   7                    1                 B          "   4   <   +   $       8         !   -      6       A                           >       3   /                  &               9   '   ;          D                        @      	   :           *   
   =   #                   ?   )          2   ,          5       %    1: No sub-navigation (flat) 2: Allow 1 level of sub-navigation 3: Allow 2 levels of sub-navigation 4: Allow 3 levels of sub-navigation A link page cannot link to another link page Advanced menu behaviour Advanced settings Always (least efficient) Auto By default, this will be used as the link text when appearing in menus. Controls how 'specific' pages objects are fetched and used when rendering this menu. This value can be overidden by supplying a different <code>use_specific</code> value to the <code>{% flat_menu %}</code> tag in your templates. Controls how 'specific' pages objects are fetched and used when rendering this menu. This value can be overidden by supplying a different <code>use_specific</code> value to the <code>{% main_menu %}</code> tag in your templates. Copy Copy this %(model_name)s Copying Copying %(model_name)s Editing Editing %(model_name)s Flat menu '{instance}' created. Flat menus For internal reference only. If checked, a link to this page will be repeated alongside it's direct children when displaying a sub-navigation for this page. If supplied, appears above the menu when rendered. Linking to both a page and custom URL is not permitted Main menu Main menu for %(site_name)s Main menu updated successfully. NOTE: The sub-menu might not be displayed, even if checked. It depends on how the menu is used in this project's templates. Off (most efficient) Optionally specify css classes to be added to this page when it appears in menus. Please choose an internal page or provide a custom URL Provide the text to use for a custom URL, or set on an internal page link to use instead of the page's title. Save Scheduled publishing Settings Site and handle must create a unique combination. A menu already exists with these same two values. The maximum number of levels to display when rendering this menu. The value can be overidden by supplying a different <code>max_levels</code> value to the <code>{% flat_menu %}</code> tag in your templates. The maximum number of levels to display when rendering this menu. The value can be overidden by supplying a different <code>max_levels</code> value to the <code>{% main_menu %}</code> tag in your templates. The menu could not be saved due to errors. This field is required when linking to a custom URL This page redirects to: %(url)s Top level Use this field to optionally specify an additional value for each menu item, which you can then reference in custom menu templates. Use this to optionally append a #hash or querystring to the URL. Use this to optionally append a #hash or querystring to the above page's URL. Used to reference this menu in templates etc. Must be unique for the selected site. allow sub-menu for this item append to URL e.g. 'Section home' or 'Overview'. If left blank, the page title will be used. flat menu flat menus handle heading link text link to a custom URL link to an internal page main menu maximum levels menu item menu item css classes menu items no. of items repeat in sub-navigation repeated item link text site specific page usage title Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2017-12-22 21:33+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: Alex <alex@efswdev.ru>, 2017
Language-Team: Russian (https://www.transifex.com/rkhleics/teams/73023/ru/)
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Language: ru
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 1: Без вложенных уровней навигации (плоское) 2: Допускаются подменю глубиной в 1 уровень 3: Допускаются подменю глубиной в 2 уровня 4: Допускаются подменю глубиной в 3 уровня Страница-ссылка не может ссылаться на другую страницу-ссылку Расширенные настройки поведения меню Расширенные настройки Всегда (наименьшая эффективность) Автоматически Это значение будет по-умолчанию использоваться как текст ссылки при появлении её в меню. Определяет, каким образом 'конкретные' объекты-страницы получаются и используются при отображении этого меню. Может быть переопределено при передаче иного значения параметра <code>use_specific</code> тэгу <code>{% flat_menu %}</code> в шаблоне. Определяет, каким образом 'конкретные' объекты-страницы получаются и используются при отображении этого меню. Может быть переопределено при передаче иного значения параметра <code>use_specific</code> тэгу <code>{% main_menu %}</code> в шаблоне. Копировать Копировать %(model_name)s Копирование Копирование %(model_name)s Редактирование Редактирование %(model_name)s Создано плоское меню '{instance}'. Плоские меню Только для внутреннего использования. Если поле отмечено, то ссылка на эту страницу будет повторяться вместе с её прямыми потомками при отображении подменю для этой страницы. Если предоставлен, то будет появляться над меню при его отображении. Недопустимо одновременно ссылаться на внутреннюю страницу и произвольный URL Главное меню Главное меню для %(site_name)s Главное меню успешно обновлено. ЗАМЕТКА: Подменю может не отображаться даже если это поле отмечено. Это будет зависеть от используемого проектом шаблона. Выключено (наибольшая эффективность) Опционально определяет CSS классы для добавления к этой странице при её появлении в меню. Пожалуйста, выберите внутреннюю страницу или предоставьте произвольный URL Используется как текст для ссылки на произвольный URL. Для ссылок на внутреннюю страницу используется вместо её заголовка. Сохранить Отложенная публикация Настройки Сайт и псевдоним должны составлять уникальную комбинацию. Уже существует меню с точно такими же значениями. Максимальное количество уровней меню, видимых при его отображении. Может быть переопределено при передаче иного значения параметра <code>max_levels</code> тэгу <code>{% flat_menu %}</code> в шаблоне. Максимальное количество уровней меню, видимых при его отображении. Может быть переопределено при передаче иного значения параметра <code>max_levels</code> тэгу <code>{% main_menu %}</code> в шаблоне. Меню не может быть сохранено из-за ошибок. Это поле необходимо для ссылок на произвольный URL Эта страница перенаправляет на %(url)s На верхнем уровне Это поле можно использовать для указания псевдонима для каждого элемента меню, чтобы затем ссылаться на него в собственных шаблонах. Это поле можно использовать для добавления к URL идентификатора #hash или строки запроса ?param=... Это поле можно использовать для добавления к указанному выше URL идентификатор #hash или строку запроса ?param=... Используется для обозначения этого меню в шаблонах и т.п. Должен быть уникальным для выбранного сайта. разрешить подменю для этого элемента дополнение к URL Например, 'Оглавление' или 'Обзор'. Если не заполнено, будет использоваться заголовок страницы. плоское меню плоские меню псевдоним заголовок меню текст ссылки ссылка на произвольный URL ссылка на внутреннюю страницу главное меню Максимальное количество уровней элемент меню CSS классы для элемента меню элементы меню Кол-во элементов повторить в подменю текст повторяемой ссылки сайт использование конкретных страниц название 