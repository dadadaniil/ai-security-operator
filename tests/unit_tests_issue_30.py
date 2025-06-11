java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UserServiceTest {

    @Mock
    private TaskService taskService;

    @Mock
    private RefreshTokenService refreshTokenService;

    @Mock
    private ConfirmationTokenService confirmationTokenService;

    @InjectMocks
    private UserService userService;

    @Test
    public void testAuthenticateUser() {
        // Arrange
        String email = "guest@example.com";
        boolean expectedResult = true;
        User user = new User("John", "Doe", email);

        when(taskService.authenticateUser(email)).thenReturn(user);

        // Act
        boolean actualResult = userService.authenticateUser(email);

        // Assert
        assertEquals(expectedResult, actualResult);
    }

    @Test
    public void testAuthenticateUserInvalidEmail() {
        // Arrange
        String email = "invalid@example.com";
        User user = null;

        when(taskService.authenticateUser(email)).thenReturn(user);

        // Act
        boolean actualResult = userService.authenticateUser(email);

        // Assert
        assertFalse(actualResult);
    }

    @Test
    public void testSaveUser() {
        // Arrange
        String email = "test@example.com";
        User user = new User("John", "Doe", email);
        Exception expectedException = null;

        when(refreshTokenService.saveUser(user)).thenThrow(new RuntimeException());

        // Act and Assert
        assertThrows(expectedException, () -> userService.saveUser(user));
    }

    @Test
    public void testSaveUserFirstNameLessThan3Symbols() {
        // Arrange
        String email = "test@example.com";
        User user = new User("J", "Doe", email);
        Exception expectedException = null;

        when(refreshTokenService.saveUser(user)).thenThrow(new RuntimeException());

        // Act and Assert
        assertThrows(expectedException, () -> userService.saveUser(user));
    }

    @Test
    public void testGetPageLinks() {
        // Arrange
        Page page = new Page();
        String expectedLink = "/users";

        when(pageLinksGenerator.getPageLinks(page)).thenReturn(expectedLink);

        // Act
        String actualLink = userService.getPageLinks(page);

        // Assert
        assertEquals(expectedLink, actualLink);
    }

    @Test
    public void testGetUserToCreatorMapper() {
        // Arrange
        User user = new User("John", "Doe", "test@example.com");
        Creator creator = new Creator();
        String expectedMapping = "{\"id\": 1, \"name\": \"John Doe\"}";

        when(userToCreatorMapper.mapUserToCreator(user)).thenReturn(creator);

        // Act
        String actualMapping = userService.getUserToCreatorMapper(user).toString();

        // Assert
        assertEquals(expectedMapping, actualMapping);
    }
}
