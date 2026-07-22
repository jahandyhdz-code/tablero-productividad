"""Script temporal para parsear el listado de tiendas y generar tiendas_catalogo.py"""
import re

RAW = """15 Oluta - Acayucan 38 Mascota Aeropuerto 41 Condesa Mexicali 43 Talpa de Allende 44 Vega de Alatorre 58 Santa Mónica 64 Perote Estadio 65 Tlaxiaca Madero 194 Los Puertos 460 Paseo las Torres 860 Rodeo 861 Cima Victoria 862 Lomas de Jarachina 864 Zaragoza-Puebla (AA)+ 868 Ciudad Cuauhtémoc 870 Quinta Nicte 887 Altar 888 Cerritos Sur 891 Xoxocotlán 893 Colinas Ciudad Victoria 981 Villa de Ahome 983 Villa Diamante 984 Macultepec 1001 San Buenaventura 1002 Teotihuacán 1004 Talleres 1005 Kabah 1006 Hospital Gral. 1008 Héroes Tecámac 1017 Quetzalcóatl 1018 Temixco 1019 San Pedrito 1023 Periférico Sur 1024 Villa de Alvarez 1025 Atlixco 1026 Las Américas 1028 Bourloug 1029 Comalcalco 1030 Amecameca 1033 Cadereyta 1034 Hermosillo Norte 1035 Forjadores 1036 Mérida Montejo 1037 Campeche Este 1038 Chetumal 1046 Cd. Valles 1049 Estadio 1051 Las Brisas 1055 Orizaba 1056 Altamirano 1057 Chilpancingo 1058 Ciudad Hidalgo 1068 Lagos de Moreno 1069 Cuauhtémoc 1071 Xilitla 1073 Ocotlán 1076 Jiutepec Fuentes 1077 Tecamachalco 1081 Ciudad Sahagún 1086 Delta 1087 Sahuayo 1088 Comitán 1089 Santa Rosa 1101 Ciudad Industrial 1103 Periférico Sur Hermosillo 1104 Tizayuca 1105 Villa Juarez 1109 Ayotla 1110 Plaza Ecatepec 1111 Álamo 1113 Puertecito de la Virgen 1120 Dr. Arroyo 1121 Axtla 1122 Capilla de Guadalupe 1124 Corales 1125 Ixmiquilpan 1132 Pátzcuaro 1133 Santa Anita Oaxaca 1142 Totoltepec 1143 Teziutlán 1150 Huehuetoca 1151 Chiautempan 1154 Arandas 1161 Valle de Chalco 1162 Tequila 1163 Atotonilco 1165 Huatusco 1166 Agua Dulce 1167 Tlapacoyan 1168 Tequisquiapan 1174 Minatitlán 1176 San Juan de los Lagos 1177 Santiago Tianguistenco 1179 Morelia Norte 1180 Tuxtepec 1181 León Echeveste 1190 Ameca Patria 1191 1193 Isla Veracruz 1194 Ixtlahuaca 1199 Tepojaco 1201 San Agustin Ecatepec 1230 Tuxtla Chico 1231 Purépero de Echaiz 1233 Tecalco 1234 Apodaca Sur 1235 Lomas de Santa Mónica 1236 Atlacomulco 1240 Gutierrez Zamora Centro 1241 Tres Valles 1243 Peribán de Ramos 1244 Pedro Escobedo 1245 Nochistlán de Mejía 1246 Salinas Victoria 1252 Instituto Tecnológico 1253 Peñaflor 1254 Acala 1276 Acajete Centro 1327 Acaxochitlán 1328 El Higo Sur 1341 Esperanza 1342 Plaza las Flores 1345 Las Brisas Cuautla 1353 Avenida Santa Isabel 1373 Cantador 1374 Gonzalez Mante 1387 5ta. Poniente 1388 Nichupté 1399 Loma Florida 1400 Joyas de Coacalco 1401 Los Sauces 1409 Ixtapa 1410 Papalotla 1411 Tuxpan 1412 Villagrán 1417 Mexicali Sur 1418 Calpulalpan 1419 Nuevo Mexicali 1420 14 Oriente 1421 Mexicali Sureste 1422 Alfredo Jimenez 1426 Coyol 1428 San Mateo Atenco 1434 Tonalá Hielera 1435 Umán Centro 1438 Acatlán de Juarez 1440 Nuevo Ideal 1444 Teloloapan 1449 Tamazula de Gordiano 1450 Ciudad Hidalgo 1465 Tepatitlán 1467 Independencia Sur 1468 Apatzingán 1470 San Pedro 1471 Navolato 1472 Meoqui 1477 Ciudad Serdán 1478 Magdalena de Kino 1479 Santa Elena 1494 Acámbaro 1497 El Caracol 1498 Plan de Guadalupe 1501 Ozumba 1502 Cuautepec 1517 Sta Rosalía de Camargo 1519 Tlalmanalco 1526 Paraíso 1539 Álamo 1540 Acatlán 1541 Miguel Aleman 1553 Huinala 1555 Parque Solidaridad 1557 Cd. Acuna 1558 La Palma 1559 San Mateo Nopala 1560 Jose Mariano Jiménez 1561 Valle Hermoso 1576 Harold Pape Monclova 1579 Calle de los Pinos 1582 Montemorelos 1583 San Quintín 1586 Ciénega de Flores 1588 San Gaspar 1589 Zacoalco 1590 Nvo. Casas Grandes 1591 San Martin Hidalgo 1593 San Marcos 1596 El Seco San Salvador 1606 Saucillo 1607 Pueblo Viejo 1611 Reynosa Centro 1614 Jamay 1633 Matatlán 1634 Cuautzingo 1647 Tala Oeste 1648 Cocula 1649 Cacahoatán 1651 Ojo Caliente 1655 Jaltenango 1660 Guamúchil 1661 Pénjamo 1663 El Manantial 1664 Mexiquense 1665 Villas Otoch 1667 Caborca 1689 Real del Bosque 1690 Aeropuerto 1691 Universidad, San Juan del Rio 1692 Jose Maria Iglesias 1693 Jalpa de Mendez 1713 Aurora 1714 16 de Septiembre 1715 Juan de la Barrera 1716 Tlajomulco 1718 Santiago Papasquiaro 1719 Villa Textil 1721 Arcelia 1728 Saraguato 1729 Plutarco Elías Calles 1753 Periférico Oriente 1755 Apaxco 1759 Zimapán 1761 Allende 1762 Cunduacán 1763 Torres del Rey 1765 Montoya 1767 Puerto de Palos 1768 El Refugio 1780 Cuitzeo 1785 Matamoros Norte 1812 Lienzo 1813 Otumba 1814 Cardel 1818 Huetamo 1820 Parras 1821 San Lorenzo 1823 Jardines de la Primavera 1826 El Carmen Tequexquitla 1828 Acolman 1829 Almoloya 1830 Arbolada los Sauces 1841 Plan de Ayala 1858 Ocosingo Sur 1863 Xalisco 1864 5 de Mayo 1867 Félix Galván 1870 Tepotzotlán 1893 Libres 1894 Central Sur 1897 San Cristóbal 1899 San Juan de la Labor 1900 Dos Ríos 1901 Oaxtepec 1921 San Mateo Atarasquillo 1922 Puerto Escondido 1923 Amalucan 1927 Puerta del Sol 1928 Estacion Nueva 1930 El Oro 1931 Lerdo 1943 Fracc. Mérida las Américas 1952 Kanasín 1954 Huamantla 1960 Guadalupe Victoria 1961 Villa Victoria 1963 Zaragoza 1975 Primer Anillo 1977 Amozoc 1978 Chilapa de Alvarez 1979 Tenango 1980 Xochitepec 1982 Blvd. Juarez 1983 Ticul 2000 Mazatlán 2006 Juchitán 2008 San Andres Tuxtla 2009 Acceso Norte 2015 Puruándiro 2017 Valle de Santiago 2018 Salvatierra 2019 Autlán de Navarro 2020 Las Choapas 2024 Ejercito Mexicano 2026 Acapulco Universidad 2027 Zacatecas 2028 Concepción del Valle 2029 Mérida Itzaes 2038 Silao 2039 Tantoyuca 2040 Panuco 2054 Terranova 2055 Zacatlán 2058 Comonfort 2059 Sayula 2062 Playa del Carmen Norte 2066 Reforma Sur 2067 Encarnación 2069 Nueva Italia 2072 Portal Chalco 2073 Nogales 2077 Reforma San Luis Potosí 2078 Matehuala 2085 Perote 2086 Apaseo El Alto 2087 Actopan 2088 Xicotepec 2096 Zumpango del Rio 2097 Pueblo Nuevo 2098 El Saucito 2099 Cortázar 2101 Nuevo Laredo Periferico 2104 Escárcega 2108 Kala 2111 Aguamilpa 2112 Av. México II 2113 Pabellón Libramiento 2114 Catemaco 2115 Mapastepec 2135 Clínica Unión del Cuatro 2136 Boulevard Morelos 2138 Delicias Sur 2141 Xonacatlán 2142 Reforma Macuspana 2144 Vicente Guerrero 2145 Norte Chignahuapan 2176 Aleman Centro 2197 Dzidzantun 2210 Acambay 2212 Ojinaga 2213 Huichapan 2215 Tasquillo 2221 Alpinismo 2222 San Jerónimo 2223 Reynosa 2224 Jilotepec 2225 Tijuana Sur 2228 La Polar 2240 Santa Cruz 2243 Navojoa 2244 La Barca 2247 Lazaro Gutiérrez 2281 Jesus Chaparro 2285 Huejotzingo 2286 Coba - Tulum 2289 Felipe Carrillo Puerto 2290 2300 Vicente 2316 Buenavista Tomatlán 2332 Tecolutilla 2340 Pie de la Cuesta 2352 Mochicahui 2355 Rio Mezquite 2358 Emilio Carranza 2362 Huajuapan 2 de Abril 2363 Cruz de Elota 2371 Guaymas Poniente 2386 Avenida Dalias 2387 Haciendas de Tizayuca 2390 Oaxaca Aeropuerto 2410 Periférico Norte Iguala 2413 Flamingos 2421 Santiago Tulantepec 2423 Atlixco Centro 2424 Aristóteles 2427 Teolocholco 2434 Tepeapulco 2449 Juan José Ríos 2450 Pueblo Yaqui 2452 Paso Limòn 2455 San Blas Batallón 2457 Altamira Sur 2459 Solidaridad Irapuato 2461 Tamayo 2469 Tixkokob 2470 Tamuin 2471 Lerdo de Tejada 2476 Nahil 2492 Del Cerrillo 2505 Anillo Periférico 2507 Rancho San Juan 2508 Salinas Hidalgo 2509 Ricardo B. Anaya 2510 Tizapán 2525 Rio Hondo 2528 Flores Magón 2529 Mieleras 2543 Eje Norponiente 2544 Primo de Verdad 2548 Avenida Universidad 2586 Rodolfo Elias Calles 2587 Cardenas 2588 Bosques de Aldama 2591 Tampico 2593 San Felipe 2594 Villa Juarez 2595 Tarimoro 2597 Cosoleacaque 2661 Durango Norte 2664 Coatepec Sur 2665 Santa Fe 2666 Jojutla 2667 Tlapa de Comonfort 2669 Santiaguito 2683 Jocotitlán 2694 Los Mochis Centro 2698 Pradera Dorada 2736 Chimalhuacán Peñón 2737 Etzatlán 2738 Mitras 2739 Carlos A. Carrillo 2740 Talámas Camandari 2741 Otilio Gonzalez 2767 Doctores 2768 Agustin Lara 2769 Hermanos Serdán 2782 Ocoyoacac 2783 Villa Guerrero 2785 Teneria 2786 Tixtla 2787 Industrias Norte 2788 Av. de las Torres 2808 Cuautlancingo 2809 Medellín II 2810 Las Fuentes 2811 Axochiapan 2812 Ajalpan 2814 Cuitláhuac 2815 Calvillo 2817 Tekax 2820 Atotonilco Sur 2823 El Oro de Hidalgo 2824 Apan 2825 Motozintla de Mendoza 2826 Jerécuaro 2828 Suchiapa Sur 2850 Jalpan Centro 2851 Hilamas 2866 Viñedos Saltillo 2868 Jardines Colon 2869 Zuazua 2871 Viento Nuevo 2873 Dimas 2875 Coatzintla 2876 Ixtaczoquitlán 2877 Calkiní 2898 Ciudad de Huitzuco 2899 Hermosillo Oriente 2908 Tierra Blanca 2910 Chuburna 2919 El Águila 2920 Saltillo Sur 2921 Mata de Pita 2922 Tepeji del Rio 2924 La Doce 2925 Colotlán 2926 Pijijiapan 2928 Santa María Centro 2929 Paso del Macho 2932 Las Trancas 2945 Valladolid 2948 Jibarito 2950 Seybaplaya 2951 Veracruz Norte 2952 San Francisco Totimehuacan 2953 El Verde 2954 El Dorado 2955 Tangancícuaro 2956 Salida A Sauceda de la Borda 2958 Armería 2977 Tonalá Plaza 2982 Villa Union Poanas 2983 Guasave Centro Saltillo 2993 Camino A Tlaltepango 2994 Duarte 2996 Salida a Sanalona 2999 Tala Ruiseñores 3000 Libramiento Taxco 3001 Av. 11 Córdoba 3002 Sumidero 3004 Huauchinango 3008 Misantla 3009 Rincón de Romos 3012 Temoaya 3013 Tempoal de Sanchez 3018 Libramiento 3019 Rincón San Antonio 3020 Xalostoc 3022 Progreso 3023 Huajuapan 3026 Gobernadora 3038 Luis Echeverría 3039 San Miguel de Allende 3040 Juan Pablo II 3041 Transistmica 3042 Santa Paula 3043 Zinacantepec 3046 Maravatío 3047 Jilotepec 3048 Jerez 3049 Teapa 3050 Valle del Mezquital 3056 Siglo XXI 3065 Bosques del Valle 3066 Antonio Rocha 3067 Salina Cruz 3068 Ciudad Rio Verde 3072 Central Gomez Palacio 3073 Multiplaza Real 3074 Villas de la Hacienda 3083 San Andres 3084 Huimanguillo 3085 Rio Grande 3088 Yurécuaro 3089 Zacualtipán 3092 Reforma Mixquiahuala 3098 Guadalupana 3099 Colima Centro 3100 Quintas del Refugio 3103 Lauro Villar 3109 Halachó 3121 Yautepec 3122 Nextlalpan 3124 Tlatlauquitepec 3126 Puente de Ixtla 3141 San Pablo Tultitlán 3142 Camino A Quiroga 3143 Los Agaves 3144 Del Prado II 3146 Chaveñas 3147 Matilde 3148 San Luis de la Paz 3150 Capultitlan 3151 San Andres Cuexcontitlan 3152 San Pablo Autopan 3153 Sombrerete 3154 Bravo 3167 Santa Inés 3173 Tejería 3174 Banderilla 3187 Camino A Tlacote 3189 Villarreal 3191 Outlet Puebla 3196 Melchor Guaspe 3197 El Grullo Oeste 3213 La Presa 3214 Chinampa 3216 Jesus Maria 3219 Juan Aldama 3220 Romita 3226 Ensenada 3227 Tuxpan Centro 3228 Manto de la Virgen 3230 Chilpancingo Norte 3231 Villas del Campo 3232 Tlaxco 3233 Mexicali Villas 3234 Tezontepec de Aldama 3238 Las Azucenas 3240 San Pablo del Monte 3243 Tacámbaro 3244 Cadereyta 3285 Enrique Estrada 3291 Salamanca Sur 3294 Nicolás Bravo 3295 Glorieta Caucel 3296 Villas de Ayotla 3297 Rio Blanco 3298 Escobedo 3301 Tepeaca 3304 Carretera Villaflores 3360 Toluquilla 3361 La Mangana 3362 Topochico 3363 Tlalcilalcalpan 3364 Tejupilco Cristóbal 3366 Coscomatepec 3367 Maneadero 3368 Guadalupe Victoria Romo 3399 Cozumel 3400 Delicias 3401 Central de Abastos 3402 Mariano Otero 3403 Paladio 3406 Puerto Peñasco 3407 San Francisco de los Romos 3408 Villa de Etla 3409 Adolfo Lopez Mateos 3411 Coatepec Harinas 3415 Azcapotzalco la Villa 3431 Plaza San Diego 3432 Hacienda la Huasteca 3442 Glorieta Apizaco 3443 Clouthier 3444 Vencedor 3485 Otay 3486 San Francisco Uruapan 3487 Tequixquiac 3514 Sahuaro 3523 Nueva Kukulcan 3524 Salagua 3526 Aeropuerto Río Colorado 3527 Chetumal Norte 3536 Manzanillo 3537 Linares 3538 Cuerámaro 3547 Pachuquilla 3548 Tehuantepec 3549 San Vicente las Palmas 3550 San Jose del Valle 3551 Izamal 3557 Chulavista 3558 Carretera de Nacajuca 3560 Panamericana 3561 Durango 3564 Jalpa 3565 Contla 3568 Berriozábal Sur 3571 Zapata Montecristo 3575 Unión de Tula 3594 La Uno 3613 El Seri 3623 Los Fresnos 3625 Diaz Berlanga 3626 Fresnillo 3628 San Miguel 3654 Villa del Carbon 3658 Balancán 3659 Tlaltenango de Sanchez Román 3660 Quiroga 3665 Canutillo 3666 Xalapa 3668 Real de Costitlan 3669 Naranjos 3670 Playa Maya 3675 Ayutla de los Libres 3676 Manuel Doblado 3677 Ario de Rosales 3678 Huatabampo 3679 Nicolás Romero 3683 Estadio Antiguo 3691 Rio Españita 3692 Valle de Lincoln 3693 Playas 3711 Benito Juarez 3713 Ruiz Cortines 3714 Mariano Hidalgo 3716 Jaral del Progreso 3722 Tulancingo 3725 Toluca Pilares 3727 Tulipanes 3729 Fundadores 3733 Satélite 3734 El Conchi 3736 Libramiento Xoxocotla 3738 Santa Cruz Atizapán 3739 Coyuca de Benítez 3743 Tula 3744 Ojo Caliente 3750 Autopista Querétaro 3751 Insurgentes Sur 3752 Vallejo 3753 Plaza Aragón 3754 Plaza Loreto 3755 Tacubaya 3756 Tlalnepantla 3757 San Juan de Aragón 3758 Calle 86 3759 San Rafael 3760 Lomas Estrella 3761 Tulyehualco 3762 Chimalhuacán 3763 Mariano Escobedo 3764 Iztapalapa 3765 Ecatepec 3766 La Viga 3767 Pachuca 3768 Villa Coapa 3769 Insurgentes Norte 3770 Pantitlán 3771 Plaza Churubusco 3772 Plaza Atizapán 3773 Vía Capu 3774 Ferrocarril Hidalgo 3775 La Aurora 3776 Sor Juana 3777 Valle de Aragón 3778 Xochimilco 3779 Acapulco Costera 3780 Atemajac 3781 Independencia 3782 Centenario 3783 Santa Clara 3784 1° de Mayo 3785 Cuautla 3786 Santa Fe 3787 Cuautitlán 3788 Margaritas 3789 Revolución 3791 Fuentes del Valle 3792 San Juanico 3793 11 Sur 3795 Texcoco 3796 Mayorazgo 3797 Cabeza de Juarez 3798 Santa Cecilia 3799 Angeles Iztapalapa 3801 Santo Domingo 3802 Convención 3803 Observatorio 3804 Hilario Medina 3805 Santa Lucia 3806 Renacimiento 3807 Saltillo 3808 Bolivar 3823 Morelos 3860 Zaragoza 3865 Villasunción 3866 Arboledas 3867 Irapuato 3868 Tihuatlan Sur 3869 Cuernavaca 3870 Morelia 3871 Plaza Cuautitlán 3874 Cantil 3875 Querétaro 3880 Plaza Dorada 3883 Melchor Ocampo 3884 Chalco 2000 3887 Rio Verde 3888 Vía Morelos 3889 San Juan del Rio 3890 La Piedad 3891 Los Reyes 3892 Av. Central 3897 La Virgen 3898 Diaz Mirón 3901 Xilotzingo 3902 Lázaro Cardenas 3903 Tehuacán 3904 Tuxtla Oriente 3905 Santa Anita 3907 Coloso Ii 3908 Tapachula 3910 Palomas 3911 Iguala 3913 Prof. Francisco Juarez 3914 Constituyentes 3916 Iztapalapa Norte 3917 Tuxtla Centro 3918 Salamanca 3919 Nicolás Zapata 3920 8 de Julio 3922 Tintero 3923 Xonaca 3924 Cofradías 3930 Las Pintas 3932 Carretera Reynosa 3934 Soledad de Doblado 3935 Santiago Tuxtla 3938 Zinapécuaro 3940 Juchitepec 3979 Cerralvo 4002 Puebla Sur 4016 Playa del Carmen 4017 Toluca Aztecas 4028 Santa Rosa N.L 4029 Av. Nacional 4032 Cintalapa 4035 Tenosique de Pino Suarez 4042 Garcia Salinas 4044 Satélite Saltillo 4045 Lomas del Bosque 4047 Sabinas Hidalgo 4058 Múzquiz 4060 Reforma Chiapas 4061 Tizimín 4065 Izúcar de Matamoros 4066 Barrancos 4067 Villa Garcia 4068 Agua Prieta 4075 Patricio Trueba 4076 Aeropuerto Zapata 4079 Huixtla 4080 Apaseo El Grande 4081 Tlaxcoapan 4083 San Miguel El Alto 4093 Jocotepec 4094 San Fernando 4113 Ciudad del Carmen 4124 Lombardía 4125 Terán 4126 Blvd. Zacatecas 4128 Arca de Noé 4129 Técpan 4130 Abasolo 4131 Hunucmá 4132 Motul 4136 Frontera 4143 Insurgentes 4144 Altotonga 4145 Acatzingo 4146 Villa Avila Camacho 4147 Nanacamilpa 4158 Obregon Poniente 4161 Comalapa 4162 Zacapoaxtla 4164 Cihuatlán 4167 Santa Rosa Jáuregui 4168 Juventino Rosas 4169 Zacatelco 4172 Calera Centro 4179 Zapotlanejo 4180 4182 Naranjos 4194 Martinez de la Torre 4195 Zacapu 4196 Sabinas 4198 El Tenayo 4199 San Luís Río Colorado 4405 Teotitlan de Flores Magon 4410 Tijuana Cd Natura 4507 Terrazas del Valle 4520 San José Vista Hermosa 4529 Constitucion Escobedo 4541 Ixtapaluca 4542 Morelia Tres Puentes 4558 Tecámac 4561 El Milagro 4564 Camargo 4568 Rio Ramos Arizpe 4570 Yahualica 4572 El Salto 4574 Loreto Centro 4577 Santa Ana 4630 Tecolotlán Lienzo Charro 4632 El Llanito 4635 Zacatlán Norte 4636 Maxcanú Norte 4639 Miramar - La Paz 4645 San Patricio Melaque 4646 Pueblitos 4649 Rincón de Romos Plaza 4650 Juchipila Norte 4664 Río Grande Sur 4669 Musaro 4672 Mazatán 4673 Esperanza Independencia 4687 Jacona de Plancarte 4689 Juan Rodríguez Clara 4704 Zaragoza Coahuila 4706 Tanquian de Escobedo 4708 Los Encinos El Marqués 4716 BD Blvd Villa de Guadalupe 4717 Villa Juárez Centro 4718 Camino Recursos Hidraulicos 4730 Las Plazas Amalucan 4731 San Luis Acaltan 4733 China NL 4743 Lázaro Cárdenas Aeropuerto 4744 Ascensión 4745 Álamos Centro 4747 Valle de los Molinos 4748 Viñedos Querétaro 4749 Cholula MBU 4763 Villas del Arco II 4776 León Centro 4777 Piedra de Agua 4778 400 - Cajeme 4785 Los Portales 4786 Luis Moya sur 4787 Taretán 4815 Camino a Cananea 4824 Camino a Calera 4825 Tesistan Centro 4829 Nueva Andalucía 4835 Juarez Tepatepec 4836 El Naranjo Norte 4837 Casimiro Castillo 4881 Haciendas Noroeste 4882 Carranza Sur 4883 Sinaloa de Leyva 4884 Cuacnopalan 4902 San Juan Zuazua 4904 Tamazunchale Norte 4905 Atana Lindavista 4907 Paseo del rey 4908 Tecamachalco Universidad 4962 Iturbide poniente 4963 Camalú 4976 Molina Enriquez 4993 Calle 50 5009 Arcos Tlachichuca 5010 Atitalaquia 5011 Camino Arandas 5013 Colina de Monte Bello 5042 Agua Blanca 5043 Chac Mool 5049 Tecozautla Sur 5059 Ezequiel Montes 5060 Glorieta Pedro Escobedo 5062 Santa Anita Cadereyta 5081 Calzada Del Sol 5083 Los Heroes 5085 Nativitas 5087 Real de Lincoln 5088 Toliman 5106 Salinas Norte 5108 Dr. Arroyo Hospital 5109 Apaseo El Grande Sur 5110 Villa Unión Federal 5114 Villa de Reyes 5116 Juventino Rosas Sur 5117 Tehuixtla 5118 Ixmiquilpan Cardonal 5119 Caborca Norte 5120 Champoton 5122 Cd. Hidalgo Sur 5123 Apaseo el Alto Sur 5124 CD Mendoza 5130 Las Norias 5131 Empalme Escobedo 5132 Real del Monte 5134 Milenio Oriente 5162 Villas del Sol 5163 Nogales Sur 5178 Alvaro Obregon 5181 Soledad De Graciano Sur 5182 Bicentenario 5183 Plaza Papasquiaro 5194 Zaragoza Huamantla 5195 Abasolo Poniente 5196 Pueblo Nuevo Centro 5198 Calpan San Andres 5214 Balvanera 5215 Cardenas Centro 5216 Plaza Calpulalpan 5219 Aviacion Las Choapas 5232 Los Reyes Plaza 5234 Platon de Sanchez 5242 Soto La Marina 5244 Tetela de Ocampo 5245 San Felipe Orizatlan 5246 Pinos Zacatecas 5247 Citara- Huehuetoca 5248 Cd Satelite 5291 Paseo Monterrey, Nuevo Laredo 5292 Ciudad Rio Bravo 5299 Nochistlan Plaza 5302 Mezquital 5303 Cañaveral 5304 La Crespa 5309 Glorieta Autlan 5333 Huandacareo 5336 Jojutla Galeana 5339 Huanímaro Oriente 5340 Plaza Yuriria 5375 Pesqueria Norte 5376 Huejotzingo 5379 Heroes Lincoln 5397 Ciruelo 5398 Bermejillo 5402 Villas del Pedregal 5430 Poncitlán 5463 Celaya Oriente 5464 Altamira Centro 5465 Av. De Las Torres Culiacán 5600 La Cañada 5604 Escuintla 5605 Estación Huehuetán 5608 Magdalena 5624 Valle Soleado 5657 Soledad de Graciano 5658 Monumento a Colosio 5659 La Ladrillera 5660 San Sebastián Tutla 5661 Lomas de la Presa 5662 Tenancingo 5665 Anáhuac 5666 Hidalgo 5667 Compostela 5668 Tuxpan Nayarit 5669 Ahualulco de Mercado 5670 Tlahuelilpan 5674 Escuinapa 5675 Javier Mina 5710 San Francisco del Rincón 5711 San Pablo 5712 Solidaridad 5713 Tlaxcala 5730 Chicoloapan 5731 Piedras Negras 5732 Tecomán 5733 Plaza Chimalhuacán 5734 Moroleón 5735 Bonfil 5736 Cardenas 5740 Belisario Domínguez 5750 Miramar 5754 Pensador Mexicano 5768 Cd Labor 5770 Zumpango 5771 Cervantes 5786 Naolinco 5792 Lourdes 5798 Santa Margarita 5799 Zihuatanejo 5800 General Miguel Atoyac 5812 Coatzacoalcos 5813 La Paz 5827 Morelia Este 5843 Uruapan 5844 Zamora 5850 Zitácuaro 5851 Constitución 6086 Actopan Olivos 6191 Santa Maria Valle 6192 Viñedos 6194 Cosalá 6195 San Rafael 6200 Bulevares del Lago 6202 Rancho Blanco 6203 Espita 6214 El Alamo Mexicali 6216 Jonuta 6230 Frontera Mexicali 6269 CD Madera 6339 Calzada Heroes Laredo 6340 Tepeaca Avenida Hidalgo 6341 Hacienda Los Eucaliptos 6346 Hidalgo del Parral 6361 La Higuera 6366 Bosques de Tecámac 6370 Villa Victoria Sur 6417 Vigas de Ramirez 6418 Amealco de Bonfil 6421 Malibran 6422 Rivera Ciudad Victoria 6448 Balancan Norte 6451 Peto 6484 Candelaria 6486 Cintalapa Oeste 6505 Las Quintas Zacatecas 6506 La Junta Norte 6507 Acatlán Jardines del Bosque 6508 Mapastepec Sur 6512 Boulevard El Refugio 6521 Hacienda Santa Fe 6522 General Teran - General Bravo 6525 Fenapo 6526 Nopalucan Norte 6582 Monte Cristal 6589 Allende Zuazua 6614 Tapilula Carretera 6616 Tamazulapam 6617 Emiliano Zapata, Morelos 6618 MISION MAGDALENA 6655 Comalcalco Villa Maya 6656 Yanga 6657 Ahuacatlán 6676 Chocaman 6681 Aculco 6683 Guadalupe Libramiento Sur 6685 Paracho 6687 Villa Bonita 6691 Puruandiro Norte 6751 Paseo Santa Isabel 6752 Miguel de la Madrid 6766 Jocotepec Chapala 6800 Revolucion Empalme 6804 Real Costa Rica 6879 Ingenio El Dorado 6883 CIUDAD GUZMAN 6916 Romita Poniente 6918 Rio Colorado"""

# Casos especiales con numeros en el nombre — se corrigen manualmente
OVERRIDES = {
    "1191": ("1191", "(Sin nombre)"),
    "1420": ("1420", "14 Oriente"),
    "1714": ("1714", "16 de Septiembre"),
    "1864": ("1864", "5 de Mayo"),
    "2290": ("2290", "(Sin nombre)"),
    "2362": ("2362", "Huajuapan 2 de Abril"),
    "3001": ("3001", "Av. 11 Córdoba"),
    "3758": ("3758", "Calle 86"),
    "3784": ("3784", "1° de Mayo"),
    "3793": ("3793", "11 Sur"),
    "3884": ("3884", "Chalco 2000"),
    "3920": ("3920", "8 de Julio"),
    "4180": ("4180", "(Sin nombre)"),
    "4778": ("4778", "400 - Cajeme"),
}

# Parsear: cada entrada empieza con un numero >= 15 seguido de texto
# Heuristica: nuevo determinante si es numero puro y el siguiente token empieza con mayuscula
# Correcciones manuales aplican despues

tokens = RAW.split()
entries = []
i = 0
current_det = None
current_parts = []

# Determinantes conocidos para validation rapida
# (si un numero aparece justo despues de otro numero + nombre, es nuevo det)
all_ints_in_text = set()
for t in tokens:
    if re.match(r'^\d+$', t):
        all_ints_in_text.add(int(t))

# Minimo determinante real
MIN_DET = 15

def is_new_det(tok, next_tok, current_det_val):
    if not re.match(r'^\d+$', tok):
        return False
    val = int(tok)
    if val < MIN_DET:
        return False
    # Si el siguiente token empieza con mayuscula o es fin de datos -> nuevo det
    if next_tok is None:
        return True
    # El siguiente token empieza con letra mayuscula (incluyendo acentuadas)
    if re.match(r'^[A-ZÁÉÍÓÚÜÑ]', next_tok):
        # Excepcion: si el valor actual es <= 16 y current_det existe
        # (para "14 Oriente", "5 de Mayo", etc.) -- son menores que los dets reales
        # Un det real siempre es >= el det anterior o razonablemente grande
        if current_det_val and val < current_det_val * 0.5:
            return False  # Es parte del nombre (ej: "14" cuando current_det=1420)
        return True
    return False

i = 0
while i < len(tokens):
    tok = tokens[i]
    next_tok = tokens[i + 1] if i + 1 < len(tokens) else None

    if current_det is None:
        # Iniciar primer entrada
        if re.match(r'^\d+$', tok) and int(tok) >= MIN_DET:
            current_det = tok
            current_parts = []
    else:
        current_det_val = int(current_det)
        if is_new_det(tok, next_tok, current_det_val):
            # Guardar entrada actual e iniciar nueva
            name = ' '.join(current_parts).strip()
            entries.append((current_det, name))
            current_det = tok
            current_parts = []
        else:
            current_parts.append(tok)
    i += 1

# Guardar ultima
if current_det:
    entries.append((current_det, ' '.join(current_parts).strip()))

# Aplicar overrides
final = []
for det, name in entries:
    if det in OVERRIDES:
        final.append(OVERRIDES[det])
    else:
        final.append((det, name))

print(f"Total tiendas parseadas: {len(final)}")
print("\nPrimeras 10:")
for d, n in final[:10]:
    print(f"  {d}: {n}")
print("\nUltimas 5:")
for d, n in final[-5:]:
    print(f"  {d}: {n}")

# Generar el archivo Python
lines = ['"""tiendas_catalogo.py — Catalogo nacional de tiendas Bodega Aurrera."""\n\n']
lines.append("# (determinante, nombre_tienda)\n")
lines.append("TIENDAS: list[tuple[str, str]] = [\n")
for det, name in final:
    safe_name = name.replace('"', '\\"')
    lines.append(f'    ("{det}", "{safe_name}"),\n')
lines.append("]\n\n")
lines.append("# Lookup rapido por determinante\n")
lines.append("TIENDAS_BY_DET: dict[str, str] = {det: nombre for det, nombre in TIENDAS}\n")
lines.append("# Lookup por nombre (normalizado)\n")
lines.append("TIENDAS_BY_NOMBRE: dict[str, str] = {nombre: det for det, nombre in TIENDAS}\n")

with open("tiendas_catalogo.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"\n Archivo tiendas_catalogo.py generado con {len(final)} tiendas.")
