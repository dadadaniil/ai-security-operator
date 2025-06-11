java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class UserServiceTest {

    @Mock
    private TaskService taskService;

    @Mock
    private RefreshTokenService refreshTokenService;

    @Mock
    private ConfirmationTokenService confirmationTokenService;

    @Mock
    private Constants constants;

    @Mock
    private UserToCreatorMapper userToCreatorMapper;

    @Mock
    private PageLinksGenerator pageLinksGenerator;

    @InjectMocks
    private UserService userService;

    @Test
    public void testGetUser() {
        when(taskService.getUser(any())).thenReturn(new User("John", "Doe"));
        assertEquals(new User("John", "Doe"), userService.getUser());
    }

    @Test
    public void testGetUserNotFound() {
        when(taskService.getUser(any())).thenReturn(null);
        assertThrows(UserNotFoundException.class, () -> userService.getUser());
    }

    @Test
    public void testSaveUser() {
        User user = new User("John", "Doe");
        when(userToCreatorMapper.map(user)).thenReturn(new Creator("John", "Doe"));
        assertEquals(new Creator("John", "Doe"), userService.saveUser(user));
    }

    @Test
    public void testSaveUserInvalidFirstName() {
        User user = new User("", "Doe");
        assertThrows(InvalidFirstNameException.class, () -> userService.saveUser(user));
    }

    @Test
    public void testRefreshToken() {
        when(refreshTokenService.refreshToken(any())).thenReturn("new-token");
        assertEquals("new-token", userService.refreshToken());
    }

    @Test
    public void testConfirmationToken() {
        when(confirmationTokenService.confirmToken(any())).thenReturn(true);
        assertEquals(true, userService.confirmationToken());
    }

    @Test
    public void testGetPageLinks() {
        when(pageLinksGenerator.generate(any())).thenReturn("page-links");
        assertEquals("page-links", userService.getPageLinks());
    }
}
