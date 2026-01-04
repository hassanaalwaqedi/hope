/// Updated Service Locator with WebSocket
import 'package:get_it/get_it.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../data/services/websocket_service.dart';

final getIt = GetIt.instance;

Future<void> setupServiceLocator() async {
  // Register WebSocket service as singleton
  getIt.registerLazySingleton<WebSocketService>(() => WebSocketService());
  
  // Register PanicBloc with injected WebSocket
  getIt.registerFactory<PanicBloc>(() => PanicBloc(
    wsService: getIt<WebSocketService>(),
  ));
}
