package io.spring.core.user;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

public class UserTest {

  private User userWithImage() {
    return new User("test@example.com", "testuser", "password", "bio", "https://example.com/avatar.png");
  }

  private User userWithoutImage() {
    return new User("test@example.com", "testuser", "password", "bio", null);
  }

  @Test
  public void hasImage_returns_true_when_image_url_is_set() {
    assertTrue(userWithImage().hasImage());
  }

  @Test
  public void hasImage_returns_false_when_image_is_null() {
    assertFalse(userWithoutImage().hasImage());
  }

  @Test
  public void hasImage_returns_false_when_image_is_blank() {
    User user = new User("test@example.com", "testuser", "password", "bio", "   ");
    assertFalse(user.hasImage());
  }

  @Test
  public void isProfileComplete_returns_true_when_bio_and_image_set() {
    assertTrue(userWithImage().isProfileComplete());
  }

  @Test
  public void isProfileComplete_returns_false_when_image_missing() {
    assertFalse(userWithoutImage().isProfileComplete());
  }

  @Test
  public void isProfileComplete_returns_false_when_bio_blank() {
    User user = new User("test@example.com", "testuser", "password", "", "https://img.example.com/a.png");
    assertFalse(user.isProfileComplete());
  }
}
