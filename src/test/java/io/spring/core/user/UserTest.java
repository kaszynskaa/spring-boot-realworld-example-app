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
  public void canBeFollowedBy_returns_true_for_different_user() {
    User user = userWithImage();
    assertTrue(user.canBeFollowedBy("other-user-id"));
  }

  @Test
  public void canBeFollowedBy_returns_false_for_null() {
    assertFalse(userWithImage().canBeFollowedBy(null));
  }

  @Test
  public void canBeFollowedBy_returns_false_for_self() {
    User user = userWithImage();
    assertFalse(user.canBeFollowedBy(user.getId()));
  }
}
