% born(name, year, sex).
% died(name, year).
% married(name1, name2, year).
% divorced(name1, name2, year).
% parents(parent1, parent2, child).

born(sergey_s, 1955, m).
born(aleksandra_s, 1960, f).
born(vladimir_a, 1950, m).
born(aleksandra_a, 1951, f).

born(aleksandr_a, 1980, m).
born(natalia_s, 1980, f).
born(evgeniy_s, 1975, m).
born(aleksandr_s, 2003, m).


born(dmitriy_a, 1977, m).
born(svetlana_a, 1980, f).
born(arseniy_a, 2006, m).
born(matvey_a, 2004, m).
born(ulana_a, 2009, f).

% тестовые персы

born(mike, 1940, m).
born(jessy, 1942, f).
born(walter, 1943, m).
born(sky, 1945, f).
born(guf, 1969, m).
born(marine, 1950, f).

born(orphan, 2007, m).
born(orphan_mom, 1990, f).
born(orphan_dad, 1980, m).
born(george, 1960, m).
born(floyd, 1972, m).

born(steve, 1950, m).
born(alex, 1952, f).
born(creeper, 1960, f).
born(sheep, 1976, f).
born(zombie, 1980, m).
born(trump, 1988, m).

married(steve, alex, 1969).
married(sergey_s, aleksandra_s, 1980).
married(vladimir_a, aleksandra_a, 1975).
married(dmitriy_a, svetlana_a, 2000).
married(orphan_dad, orphan_mom, 2007).
married(mike, jessy, 1960).
married(mike, marine, 1981).
married(jessy, walter, 1982).
married(walter, sky, 1989).
married(steve, creeper, 1975).
married(zombie, sheep, 1985).
married(evgeniy_s, natalia_s, 2000).

parents(zombie, sheep, trump).
parents(steve, creeper, sheep).
parents(steve, alex, aleksandra_a).
parents(george, marine, vladimir_a).
parents(mike, jessy, aleksandra_s).
parents(mike, jessy, orphan_mom).
parents(mike, jessy, orphan_dad).
parents(evgeniy_s, natalia_s, aleksandr_s).
parents(sergey_s, aleksandra_s, svetlana_a).
parents(sergey_s, aleksandra_s, natalia_s).
parents(vladimir_a, aleksandra_a, dmitriy_a).
parents(vladimir_a, aleksandra_a, aleksandr_a).
parents(dmitriy_a, svetlana_a, arseniy_a).
parents(dmitriy_a, svetlana_a, matvey_a).
parents(dmitriy_a, svetlana_a, ulana_a).
parents(orphan_dad, orphan_mom, orphan).
parents(jessy, walter, george).
parents(walter, sky, guf).
parents(walter, sky, floyd).

died(trump, 2025).
died(sergey_s, 2005).
died(evgeniy_s, 2010).
died(orphan_dad, 2008).
died(orphan_mom, 2012).
died(mike, 1985).
died(jessy, 1988).
died(walter, 2000).
died(steve, 2007).
died(zombie, 2020).

divorced(mike, jessy, 1980).
divorced(sergey_s, aleksandra_s, 2010).
divorced(orphan_mom, orphan_dad, 2008).
divorced(jessy, walter, 1988).
divorced(walter, sky, 1999).
divorced(steve, alex, 1970).
divorced(zombie, sheep, 2000).


% жив ли такой то персонаж в таком то году
alive(Person, Year) :-
	number(Year),
	Year =< 2025,
	born(Person, BirthYear, _),
	BirthYear =< Year,
	( \+ died(Person, _) ; (died(Person, DiedYear), DiedYear > Year)).

% true, если Parent является одним из родителей Child
parent_of(P, C) :-
    parents(P, _, C) ; parents(_, P, C).
    
% человек - мужчина?
male(Person) :-
    born(Person, _, m).

% человек - женщина?
female(Person) :-
	born(Person, _, f).

% нахождение отца ребенка
father(F, Child) :-
	parent_of(F, Child),
	male(F).

% нахождение матери ребенка
mother(M, Child) :-
	parent_of(M, Child),
	female(M).

% полные братья или сестры: (оба родителя)
full_sibling(X, Y) :-
	X \= Y,
    mother(M, X), mother(M, Y),
    father(F, X), father(F, Y).

% один общий родитель
half_sibling(X, Y) :-
    X \= Y,
    (
        (mother(M, X), mother(M, Y), \+ full_sibling(X, Y))
        ;
        (father(F, X), father(F, Y), \+ full_sibling(X, Y))
    ).

% хотя бы 1 общий родитель
sibling(X, Y) :-
    X \= Y,
    parent_of(P, X),
    parent_of(P, Y).

% нахождение сестер
sisters(X, Y):-
	female(X),
	female(Y),
	full_sibling(X, Y).

% нахождение братьев
brothers(X, Y):-
	male(X),
	male(Y),
	full_sibling(X, Y).
	
% женаты ли всю жизнь
is_married(Wife, Husband):-
	married(Wife, Husband, _) ; married(Husband, Wife, _),
	\+ divorced(Wife, Husband, _) ; \+ divorced(Husband, Wife, _).

% найти мужа
husband(Wife, Husband):-
	female(Wife),
	is_married(Wife, Husband),
	male(Husband).

% найти жену
wife(Husband, Wife):-
	male(Husband),
	is_married(Husband, Wife),
	female(Wife).

% двоюродные братья и сестры
cousins(X, Y):-
	\+ sibling(X, Y),
	parent_of(P1, X),
	parent_of(P2, Y),
	full_sibling(P1, P2).

% двоюродные сестры
cousins_sisters(X, Y):-
	female(X),
	female(Y),
	cousins(X, Y).

% двоюродные братья
cousins_brothers(X, Y):-
	male(X),
	male(Y),
	cousins(X, Y).

% бабушки дедушки
grandparent(Child, Grandparent) :-
	parent_of(Parent, Child),
	parent_of(Grandparent, Parent).

% бабушки
grandmother(Child, Grandmother):-
	female(Grandmother),
	grandparent(Child, Grandmother).

% дедушки
grandfather(Child, Grandfather):-
	male(Grandfather),
	grandparent(Child, Grandfather).

% универсальная проверка на брак (без разницы кто идет первый)
married_univ(X, Y, Year):-
	married(X, Y, Year) ; married(Y, X, Year).

% женаты ли в такой год
married_in(X, Y, Year):-
	married_univ(X, Y, MarryYear),
	Year >= MarryYear,
	(\+divorced(X, Y, _) ; (divorced(X, Y, DivYear), DivYear > Year)).

% дети в такой то год
childrens_in(Parent, Child, Year):-
	born(Child, BornYear, _),
	BornYear =< Year,
	parent_of(Parent, Child).

% сыновья в такой то год
sons_in(Parent, Boy, Year):-
	male(Boy),
	childrens_in(Parent, Boy, Year).

% дочери в такой то год
daugthers_in(Parent, Girl, Year):-
	male(Girl),
	childrens_in(Parent, Girl, Year).

% сирота ли в такой то год
orphan_in(Child, Year):-
	born(Child, BornYear, _),
	BornYear =< Year,
	parent_of(P1, Child),
	parent_of(P2, Child),
	P1 \= P2,
	died(P1, P1Y),
	died(P2, P2Y),
	P1Y =< Year,
	P2Y =< Year.

% дяди
uncle(Uncle, Child) :-
    parent_of(Parent, Child),
    brothers(Uncle, Parent).

% тети
aunt(Aunt, Child) :-
    parent_of(Parent, Child),
    sisters(Aunt, Parent).

% внуки внучки
grandchild(Grandparent, Grandchild) :-
    parent_of(Parent, Grandchild),
    parent_of(Grandparent, Parent).

% кол-во детей к такому то году
children_count_in(Parent, Year, Count) :-
    findall(Child, childrens_in(Parent, Child, Year), Children),
    length(Children, Count).

% кол-во братьев к такому то году
brothers_count_in(X, Year, Count) :-
    findall(Bro, (brothers(X, Bro), born(Bro, BY, _), BY =< Year), Bros),
    length(Bros, Count).

% кол-во систер к такому то году
sisters_count_in(X, Year, Count) :-
    findall(Sis, (sisters(X, Sis), born(Sis, BY, _), BY =< Year), Siss),
    length(Siss, Count).