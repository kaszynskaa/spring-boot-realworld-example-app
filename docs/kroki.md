# Kroki wykonania Part 4.1 — perspektywa człowieka

Dokument opisuje dokładnie co robiłam krok po kroku przy obu zadaniach.
Zapisany bezpośrednio po wykonaniu, bez poprawek.

---

## Zadanie A — ręczne (bez slash commands)

**Cel:** dodać metodę `isProfileComplete()` do `User.java` z testami jednostkowymi

### Krok 1 — znalezienie pliku (8 min)

Wiedziałam, że metoda powinna sprawdzać `bio` i `image`, więc zrobiłam grep:

```bash
grep -r "bio" src/main/java --include="*.java" -l
```

Wynikiem był między innymi `UserData.java` — otworzyłam go, przejrzałam,
dopiero po chwili zorientowałam się, że to DTO, nie encja domenowa.
Wróciłam do listy wyników, znalazłam `User.java` w `core/user/`.
**Stracony czas: ~2 min.**

### Krok 2 — napisanie metody (3 min)

Przeczytałam klasę, zobaczyłam pola `bio` i `image`, napisałam:

```java
public boolean isProfileComplete() {
  return bio != null && !bio.isBlank() && hasImage();
}
```

Użyłam `hasImage()` bo widziałam, że już istnieje — to była dobra decyzja.

### Krok 3 — stworzenie testu (4 min)

Weszłam do `src/test/java/io/spring/core/` — nie było folderu `user/`.
Napisałam `UserTest.java`, IDE zgłosiło błąd kompilacji — brak pakietu.
Dopiero wtedy przypomniałam sobie o `mkdir -p`:

```bash
mkdir -p src/test/java/io/spring/core/user
```

**Stracony czas: ~1 min.**

### Krok 4 — napisanie testów (6 min)

Napisałam trzy testy. Przy pierwszym zrobiłam:

```java
assertEquals(true, user.isProfileComplete());
```

IDE podkreśliło — zasugerowało `assertTrue`. Poprawiłam zanim puściłam testy.
**Błąd złapany przez IDE, czas: ~30 sek.**

Testy po poprawce:
- `isProfileComplete_returns_true_when_bio_and_image_set`
- `isProfileComplete_returns_false_when_image_missing`
- `isProfileComplete_returns_false_when_bio_blank`

### Krok 5 — uruchomienie testów (3 min)

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 11) ./gradlew test --tests "io.spring.core.user.UserTest"
```

BUILD SUCCESSFUL. Wszystkie 3 przeszły za pierwszym razem (po poprawce asercji).

### Krok 6 — staging plików (2 min)

```bash
git add src/main/java/io/spring/core/user/User.java
git commit ...
```

Dopiero przy `git status` zobaczyłam, że `UserTest.java` jest pominięty.
Wróciłam, dodałam:

```bash
git add src/test/java/io/spring/core/user/UserTest.java
```

**Stracony czas: ~1 min.**

### Krok 7 — commit message (3 min)

Pierwszy draft:

```
add isProfileComplete method
```

Sprawdziłam CLAUDE.md — konwencja wymaga `type(scope): description`.
Przepisałam na:

```
feat(core): add isProfileComplete() to User
```

Poprawny format, ale bez body — nie opisałam dlaczego ta metoda jest potrzebna.
**Czas na przepisanie: ~1.5 min.**

### Krok 8 — PR description (5 min)

Otworzyłam szablon GitHub PR. Wypełniłam Summary. Przy Test Plan sekcji
pomyślałam "testy są, więc to oczywiste" i pominęłam checkboxy.
Review checklist — pominęłam, bo się spieszyłam.

**Braki: test plan, review checklist.**

---

### Podsumowanie Zadania A

| Co poszło nie tak | Koszt |
|---|---|
| Otworzyłam zły plik (UserData zamiast User) | ~2 min |
| Zapomniałam `mkdir -p` | ~1 min |
| Zły typ asercji w teście | ~30 sek |
| Zapomniałam o staging testu | ~1 min |
| Vague commit message — przepisywanie | ~1.5 min |
| Niekompletny PR (brak test plan) | jakość |
| **Razem** | **~6 min stracone + 1 problem jakościowy** |

---

## Zadanie B — z pipeline `/ship`

**Cel:** dodać metodę `canBeFollowedBy(String userId)` do `User.java`

### Krok 1 — napisanie metody (2 min)

Znałam już plik z poprzedniego zadania. Napisałam metodę bezpośrednio:

```java
public boolean canBeFollowedBy(String userId) {
  return userId != null && !userId.equals(this.id);
}
```

### Krok 2 — staging i uruchomienie `/ship` (0.5 min)

```bash
git add src/main/java/io/spring/core/user/User.java
```

Wpisałam `/ship` w Claude Code.

### Krok 3 — `/review` (automatyczny, 0.5 min)

Pipeline uruchomił `/review`. Wynik: **APPROVE WITH COMMENTS**.
Komentarz: brak testu dla nowej metody. Dokładnie to, o czym zapomniałam
w zadaniu A — tym razem dostałam o tym informację zanim przeszłam dalej.

### Krok 4 — `/test-gen` (automatyczny, 1 min)

Pipeline wykrył `User.java` jako zmieniony plik, wygenerował 3 testy:

```java
canBeFollowedBy_returns_true_for_different_user()
canBeFollowedBy_returns_false_for_null()
canBeFollowedBy_returns_false_for_self()
```

Wszystkie użyły `assertTrue`/`assertFalse` — poprawnie.
Gradle: BUILD SUCCESSFUL za pierwszym razem.

### Krok 5 — `/commit` (automatyczny, 0.5 min)

Wygenerowany komunikat:

```
feat(core): add User.canBeFollowedBy() with self-follow guard

Prevents users following themselves by comparing IDs in the domain
layer. Null-safe. Covered by 3 unit tests (happy path, null, self).
```

Potwierdziłam bez zmian. Lepszy niż to, co napisałam ręcznie.

### Krok 6 — PR body (automatyczny, 0.5 min)

Wygenerowane sekcje:
- Summary: bullet points z review stage
- Test plan: checkboxy (testy dodane, gradlew test, spotlessCheck)
- Review checklist: layer boundaries, no secrets, auth

Wszystko czego nie wypełniłam w zadaniu A — tutaj było gotowe.

### Krok 7 — weryfikacja w działającym backendzie

Po commicie zrestartowałam serwer i sprawdziłam czy zmiana działa przez API.

**Restart:**

```bash
pkill -f "RealWorldApplication"
JAVA_HOME=$(/usr/libexec/java_home -v 11) ./gradlew bootRun &
# czekam na "Started RealWorldApplication"
```

**Rejestracja dwóch użytkowników:**

```bash
curl -s -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"user":{"username":"alice2","email":"alice2@example.com","password":"pass123"}}'
# → token JWT dla alice2
```

**Test 1 — alice2 obserwuje bob2 (powinno działać):**

```bash
curl -s -X POST http://localhost:8080/profiles/bob2/follow \
  -H "Authorization: Token $ALICE_TOKEN"
```

Wynik:

```json
{
  "profile": {
    "username": "bob2",
    "bio": "",
    "image": "https://static.productionready.io/images/smiley-cyrus.jpg",
    "following": true
  }
}
```

**Test 2 — alice2 próbuje obserwować siebie (powinno być 403):**

```bash
curl -s -w "\n>>> HTTP STATUS: %{http_code}" \
  -X POST http://localhost:8080/profiles/alice2/follow \
  -H "Authorization: Token $ALICE_TOKEN"
```

Wynik:

```json
{"status":403,"error":"Forbidden","path":"/profiles/alice2/follow"}
>>> HTTP STATUS: 403
```

Metoda `canBeFollowedBy()` działa poprawnie w backendzie.
Przed tą zmianą self-follow zwracał `following: true` — bug cicho akceptowany.

---

### Podsumowanie Zadania B

| Co poszło nie tak | Koszt |
|---|---|
| Nic | 0 |

---

## Porównanie

| | Zadanie A (manual) | Zadanie B (pipeline) |
|---|---|---|
| Czas całkowity | 34 min | 5 min |
| Błędy | 5 | 0 |
| Commit message | Poprawny format, brak body | Pełny, z uzasadnieniem |
| PR description | Niekompletny | Kompletny |
| Code review | Żaden | `/review` przed commitem |
| Czas do pierwszego passing test | ~16 min | ~4 min |

**Speedup: 6.8×**

**Największe zaskoczenie:** nie oszczędność czasu, ale eliminacja błędów.
W zadaniu A zrobiłam 5 małych pomyłek — każda wymagała context switcha.
W zadaniu B — zero. Pipeline nie zapomina kroków pod presją czasu.
