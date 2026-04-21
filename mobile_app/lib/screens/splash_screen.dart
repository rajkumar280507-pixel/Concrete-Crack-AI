import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'home_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateToHome();
  }

  void _navigateToHome() async {
    // Artificial delay for splash animation
    await Future.delayed(const Duration(seconds: 4));
    if (!mounted) return;
    
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const HomeScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Project Loading Animation (Lottie)
            SizedBox(
              height: 200,
              child: Lottie.network(
                'https://assets9.lottiefiles.com/packages/lf20_at6p7bti.json', // AI scan animation
                fit: BoxFit.contain,
              ),
            ),
            const SizedBox(height: 32),
            const Text(
              "CCIS",
              style: TextStyle(
                color: Colors.cyanAccent,
                fontSize: 32,
                fontWeight: FontWeight.bold,
                letterSpacing: 4,
              ),
            ),
            const Text(
              "CONCRETE CRACK INTELLIGENCE SUITE",
              style: TextStyle(
                color: Colors.white60,
                fontSize: 10,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 100),
            const CircularProgressIndicator(
              color: Colors.cyanAccent,
              strokeWidth: 2,
            ),
          ],
        ),
      ),
    );
  }
}
